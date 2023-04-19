import model
import view
import controller

if __name__ == "__main__":
    game = controller.TankWarsController(model, view)
    game.start()
