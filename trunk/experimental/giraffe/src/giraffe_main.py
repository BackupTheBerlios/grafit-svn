from project import Project
from worksheet import Worksheet
from ui.main import Application

def main():
    p = Project()
    app = Application(p)
    app.run()

if __name__ == '__main__':
    main()
