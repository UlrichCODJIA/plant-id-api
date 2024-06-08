import os
from flask import Flask, request, jsonify, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_jwt_extended import (
    JWTManager,
    get_jwt_identity,
    jwt_required,
    verify_jwt_in_request,
)
from werkzeug.utils import secure_filename
from prometheus_flask_exporter import PrometheusMetrics
from flasgger import Swagger
from plantnet import PlantNetAPI
from utils import allowed_file, get_logger
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


limiter = Limiter(
    key_func=lambda: (
        get_jwt_identity()
        if verify_jwt_in_request(optional=True)
        else get_remote_address()
    )
)
limiter.init_app(app)

cache = Cache(app)

logger = get_logger(__name__)

metrics = PrometheusMetrics(app)

plantnet_api = PlantNetAPI(
    app.config["PLANTNET_API_KEY"], app.config["PLANTNET_API_ENDPOINT"]
)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Plant Identification API",
        "description": "API for identifying plant species based on uploaded images",
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token for authentication. Example: 'Bearer {token}'",
        }
    },
    "security": [{"Bearer": []}],
}

swagger = Swagger(app, template=swagger_template)

jwt = JWTManager(app)


@app.route("/api/identify", methods=["POST"])
@limiter.limit(app.config["RATELIMIT_DEFAULT"])
@jwt_required()
def identify_plant():
    """
    Identify plant species based on uploaded images.

    ---
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: Image file(s) of the plant to be identified (up to 5 images).
      - name: organ_1
        in: formData
        type: string
        required: false
        description: Organ of the plant in the first image.
      - name: organ_2
        in: formData
        type: string
        required: false
        description: Organ of the plant in the second image.
      - name: organ_3
        in: formData
        type: string
        required: false
        description: Organ of the plant in the third image.
      - name: organ_4
        in: formData
        type: string
        required: false
        description: Organ of the plant in the fourth image.
      - name: organ_5
        in: formData
        type: string
        required: false
        description: Organ of the plant in the fifth image.

    responses:
      200:
        description: Successful plant identification.
        schema:
          $ref: '#/definitions/IdentificationResult'
      400:
        description: Bad request (missing or invalid parameters).
      401:
        description: Unauthorized (missing or invalid authentication token).
      429:
        description: Too many requests (rate limit exceeded).
      500:
        description: Internal server error.

    definitions:
      IdentificationResult:
        type: object
        properties:
          results:
            type: array
            items:
              $ref: '#/definitions/PlantMatch'
      PlantMatch:
        type: object
        properties:
          species:
            type: object
            properties:
              scientificNameWithoutAuthor:
                type: string
              scientificNameAuthorship:
                type: string
              genus:
                type: object
                properties:
                  scientificNameWithoutAuthor:
                    type: string
                  scientificNameAuthorship:
                    type: string
              family:
                type: object
                properties:
                  scientificNameWithoutAuthor:
                    type: string
                  scientificNameAuthorship:
                    type: string
              commonNames:
                type: array
                items:
                  type: string
          score:
            type: number
    """
    if "image" not in request.files:
        abort(400, description="No image file found")

    images = request.files.getlist("image")

    if len(images) > app.config["MAX_IMAGES"]:
        abort(
            400,
            description=f"You can upload up to {app.config['MAX_IMAGES']} images only",
        )

    for image_file in images:
        if not allowed_file(image_file.filename):
            abort(400, description="Invalid file extension")
        if image_file.content_type not in app.config["ALLOWED_CONTENT_TYPES"]:
            abort(400, description="Invalid file content type")

    files = []
    organs = []
    for idx, image_file in enumerate(images):
        organ = request.form.get(f"organ_{idx+1}", "auto")
        organs.append(organ)
        files.append(
            (
                "images",
                (
                    secure_filename(image_file.filename),
                    image_file.stream,
                    image_file.mimetype,
                ),
            )
        )

    data = {"organs": organs}

    try:
        cache_key = f"identification_{hash(tuple(files))}"
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info("Returning cached identification result")
            return jsonify(cached_result), 200

        json_result = plantnet_api.identify(files, data)["results"][0]

        cache.set(cache_key, json_result, timeout=app.config["CACHE_DEFAULT_TIMEOUT"])

        logger.info("Plant identification successful")
        return jsonify(json_result), 200

    except Exception as e:
        logger.exception("Error during plant identification")
        abort(500, description="An error occurred during plant identification")


@app.errorhandler(400)
def bad_request(error):
    """
    Custom error handler for 400 Bad Request.
    """
    return jsonify({"error": error.description}), 400


@app.errorhandler(401)
def unauthorized(error):
    """
    Custom error handler for 401 Unauthorized.
    """
    return jsonify({"error": error.description}), 401


@app.errorhandler(404)
def not_found(error):
    """
    Custom error handler for 404 Not Found.
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(429)
def rate_limit_exceeded(error):
    """
    Custom error handler for 429 Too Many Requests.
    """
    return jsonify({"error": "Rate limit exceeded"}), 429


@app.errorhandler(500)
def internal_server_error(error):
    """
    Custom error handler for 500 Internal Server Error.
    """
    return jsonify({"error": error.description}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
