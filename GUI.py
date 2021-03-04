import PySimpleGUI as sg
from age_rating_finder import find_game

sg.theme('Light Green')

layout = [[sg.Text("Enter game title")],
          [sg.Input()],
          [sg.Button('Get ratings')]]

window = sg.Window('Games age rating finder', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    game_ratings = find_game(values[0])
    header = [[sg.Text('Rating source', size=(15, 2)), sg.Text('Age rating', size=(15, 2))]]
    input_rows = [[sg.Text(source, size=(15, 1)), sg.Text(age, size=(15, 1))]
                  for source, age in game_ratings]
    layout = header + input_rows
    window = sg.Window('Game age ratings', layout)