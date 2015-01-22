import pyggel
from pyggel import view

def main():

    v = view.View()

    v.background_color = (1,0,0,1)

    v.build()
    v.set3d()

    v.clear_screen()
    v.refresh_screen()

main()
