from main import Game

if __name__ == "__main__":
    try:
        game = Game()
        while True:
            game.new()
            game.run()
    except Exception as e:
        print(f"Error: {e}")
        input("Presiona Enter para salir...")