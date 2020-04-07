from main import app, Unauthorized, NotFound, BadRequest, jsonify


@app.errorhandler(400)
def Unauthorized(error):
    return jsonify({"message": "You are not authorized"})


@app.errorhandler(404)
def NotFound(error):
    return jsonify({"message": "the resource you requested is not availabe"})


@app.errorhandler(400)
def BadRequest(error):
    return jsonify({"message": "that was a bad request"})
