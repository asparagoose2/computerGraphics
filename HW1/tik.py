import tkinter as tk
import tkinter.colorchooser as cc

DAFAULT_COLOR_THEME = ["#cdb4db","#ffc8dd","#ffafcc","#bde0fe","#a2d2ff"]


def create_color_picker_window():
    # Create a window and set its title
    root = tk.Tk()
    root.title("Color Picker")
    root.geometry("400x600")
    # Create a list to store the selected colors
    selected_colors = [None] * 4

    # Create a function to apply the selected color
    def apply_color(index):
        hex_color = color_labels[index].cget("bg")

        # Show a color picker dialog to let the user choose a color
        selected_color = cc.askcolor(color=hex_color, title="Choose a color")

        # Set the background of the label to the selected color
        if selected_color:
            color_labels[index].configure(bg=selected_color[1])
            selected_colors[index] = selected_color[1]

    title_label = tk.Label(root, text="Select 4 colors")
    title_label.pack()

    # Create 4 Labels to display the selected colors
    color_labels = []
    for i in range(4):
        color_label = tk.Label(root, text="Color {}".format(i+1), bg=DAFAULT_COLOR_THEME[i], width=20, height=3)
        color_label.bind("<Button-1>", lambda event, i=i: apply_color(i))
        color_labels.append(color_label)


    # Pack the widgets into the window
    for i in range(4):
        color_labels[i].pack(padx=10, pady=10)

    # Create a function to handle closing the window
    def close_window():
        # Store the selected colors in a file
        with open("selected_colors.txt", "w") as f:
            f.write("\n".join(selected_colors))

        # Close the window
        root.destroy()

    # Create a Button to close the window
    close_button = tk.Button(root, text="Apply", command=close_window)
    close_button.pack(padx=10, pady=10)

    # Start the event loop
    root.mainloop()

if __name__ == "__main__":
    create_color_picker_window()