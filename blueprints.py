from controllers.usuario_controller import usuario_bp
from controllers.game_controller import game_bp

def register_blueprints(app):
    app.register_blueprint(usuario_bp)
    app.register_blueprint(game_bp)
