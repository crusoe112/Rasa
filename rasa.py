import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter import filedialog, simpledialog, ttk
from tkhtmlview import HTMLScrolledText
import markdown
import os

class FileMenu:
    def __init__(self, parent, editor):
        self.editor = editor
        self.file_menu = tk.Menu(parent)
        parent.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New File", command=editor.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open", command=editor.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=editor.save_file, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Quit", command=root.quit, accelerator="Ctrl+Q")
        parent.bind_all("<Control-n>", lambda event: editor.new_file())
        parent.bind_all("<Control-o>", lambda event: editor.open_file())
        parent.bind_all("<Control-s>", lambda event: editor.save_file())
        parent.bind_all("<Control-q>", lambda event: root.quit())

        # Add a preferences command
        self.file_menu.add_command(label="Preferences", command=self.open_preferences_window)

    def open_preferences_window(self):
        # Create a new window
        self.preferences_window = tk.Toplevel(self.editor.root)
        self.preferences_window.title("Preferences")

        # Add options to select background and font colors
        tk.Button(self.preferences_window, text="Select Background Color", command=self.select_bg_color).pack()
        tk.Button(self.preferences_window, text="Select Font Color", command=self.select_font_color).pack()
        tk.Button(self.preferences_window, text="Select Timer Color", command=self.select_timer_color).pack()

    def select_bg_color(self):
        # Use a color dialog to select a color
        color = askcolor()[1]
        if color is not None:
            self.editor.text.config(bg=color)
            self.editor.root.config(bg=color)
            self.editor.timer_widget.change_bg_color()

    def select_font_color(self):
        # Use a color dialog to select a color
        color = askcolor()[1]
        if color is not None:
            self.editor.text.config(fg=color)
            self.editor.timer_widget.change_text_color()

    def select_timer_color(self):
        # Use a color dialog to select a color
        color = askcolor()[1]
        if color is not None:
            self.editor.timer_widget.change_timer_color(color)

class EditMenu:
    def __init__(self, parent, editor):
        self.edit_menu = tk.Menu(parent)
        parent.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Undo", command=editor.text.edit_undo, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="Redo", command=editor.text.edit_redo, accelerator="Ctrl+Y")
        parent.bind_all("<Control-z>", lambda event: editor.text.edit_undo())
        parent.bind_all("<Control-y>", lambda event: editor.text.edit_redo())

class ViewMenu:
    def __init__(self, parent, editor):
        self.editor = editor
        self.view_menu = tk.Menu(parent)
        parent.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Distraction Free Mode", command=editor.distraction_free, accelerator="Ctrl+D")
        self.view_menu.add_command(label="Dark Mode", command=editor.dark_mode, accelerator="Ctrl+K")
        self.view_menu.add_command(label="Toggle Rendered Markdown", command=editor.toggle_render_markdown, accelerator="Ctrl+M")
        parent.bind_all("<Control-d>", lambda event: editor.distraction_free())
        parent.bind_all("<Control-k>", lambda event: editor.dark_mode())
        parent.bind_all("<Control-m>", lambda event: editor.toggle_render_markdown())

class TimerMenu:
    def __init__(self, parent, timer_widget):
        self.timer_widget = timer_widget
        self.timer_menu = tk.Menu(parent)
        parent.add_cascade(label="Timer", menu=self.timer_menu)
        self.timer_menu.add_command(label="Start Timer", command=timer_widget.start_timer, accelerator="Ctrl+B")
        self.timer_menu.add_command(label="Stop Timer", command=timer_widget.stop_timer, accelerator="Ctrl+P")
        self.timer_menu.add_command(label="Set Timer", command=timer_widget.set_timer, accelerator="Ctrl+R")
        self.timer_visibility = tk.BooleanVar()
        self.timer_visibility.set(False)
        self.timer_menu.add_checkbutton(label="Show Timer", variable=self.timer_visibility, command=self.timer_widget.toggle_visibility, accelerator="Ctrl+J")
        parent.bind_all("<Control-b>", lambda event: timer_widget.start_timer())
        parent.bind_all("<Control-p>", lambda event: timer_widget.stop_timer())
        parent.bind_all("<Control-r>", lambda event: timer_widget.set_timer())
        parent.bind_all("<Control-j>", lambda event: timer_widget.toggle_visibility())

class CircularProgressBar:
    def __init__(self, parent, editor):
        self.editor = editor
        self.bg_color = '#0f0a20' if editor.dark_mode_on else '#fdfdfd'
        self.text_color = '#fdfdfd' if editor.dark_mode_on else '#0f0a20'
        self.canvas = tk.Canvas(parent, width=80, height=80, bg=self.bg_color, bd=0, highlightthickness=0)
        self.total_seconds = 25 * 60
        self.timer_seconds = self.total_seconds
        self.icon = ''
        self.color = '#0f0a20'

        self.visible = False  # The timer is not visible by default
        self.running = False

        # Bind the click event to the canvas
        self.canvas.bind("<Button-1>", self.toggle_timer)
        # Bind the enter and leave events to the canvas
        self.canvas.bind("<Enter>", self.show_icon)
        self.canvas.bind("<Leave>", self.hide_icon)

    def toggle_timer(self, event):
        if self.timer_seconds <= 0:
            self.timer_seconds = self.total_seconds
            self.icon = '>'
            self.running = False
        elif self.running:
            self.stop_timer()
            self.icon = ">"
        else:
            self.start_timer(self.total_seconds, self.timer_seconds)
            self.icon = "||"
        self.render()

    def show_icon(self, event):
        # Show a pause or play icon depending on whether the timer is running
        if self.timer_seconds <= 0:
            self.icon = '<<'
        elif self.running:
            self.icon = "||"
        else:
            self.icon = ">"
        self.render()

    def hide_icon(self, event):
        # Redraw the timer to hide the icon
        self.icon = ''
        self.render()

    def start_timer(self, total_seconds, timer_seconds):
        if self.running:
            return
        self.timer_seconds = timer_seconds
        self.total_seconds = total_seconds
        self.running = True
        self.update_timer()

    def stop_timer(self):
        if not self.running:
            return
        self.running = False
        self.render()

    def render(self):
        self.canvas.delete('all')  # Clear the canvas
        self.canvas.config(bg=self.bg_color)
        # Calculate the angle

        # Draw the text
        if self.timer_seconds >= 0:
            angle = self.timer_seconds / self.total_seconds * 360
            if angle == 360:
                angle = 359.99
            # Draw the arc (foreground)
            self.canvas.create_arc(10, 10, 70, 70, start=90, extent=angle, width=2, outline=self.color, style='arc')
            if self.icon == '':
                time_text = f"{self.timer_seconds//60}:{self.timer_seconds%60:02}"
                font_size = 12 if len(time_text) <= 4 else 10  # Adjust the font size based on the length of the time_text
                self.canvas.create_text(40, 40, text=time_text, fill=self.text_color, font=("Dejavu Sans Mono", font_size, 'bold'))
            else:
                self.canvas.create_text(40, 40, text=self.icon, fill=self.text_color, font=("Dejavu Sans Mono", 24, 'bold'))
        else:
            self.running = False
            self.canvas.delete('all')  # Clear the canvas
            if self.icon == '':
                self.canvas.create_text(40, 40, text="Time's up!", fill=self.text_color, font=("Dejavu Sans Mono", 10, 'bold'))
            else:
                self.canvas.create_text(40, 40, text=self.icon, fill=self.text_color, font=("Dejavu Sans Mono", 24, 'bold'))


    def update_timer(self):
        self.render()

        if self.running:
            self.timer_seconds -= 1
            self.canvas.after(1000, self.update_timer)  # Schedule the next update

    def toggle_dark_mode(self):
        self.bg_color = '#fdfdfd' if self.editor.dark_mode_on else '#0f0a20'
        self.text_color = '#0f0a20' if self.editor.dark_mode_on else '#fdfdfd'
        self.color = '#0f0a20' if self.editor.dark_mode_on else '#9084f0'
        self.canvas.config(bg=self.bg_color)
        self.render()

    def change_bg_color(self):
        self.bg_color = self.editor.text.cget('bg')
        self.render()

    def change_text_color(self):
        self.text_color = self.editor.text.cget('fg')
        self.render()

    def change_timer_color(self, color):
        self.color = color
        self.render()

    def toggle_visibility(self):  # Add this method
        if self.visible:
            self.canvas.place_forget()
            self.visible = False
        else:
            self.canvas.place(relx=0.997, rely=0.003, anchor='ne')
            self.visible = True
            self.timer_seconds = self.total_seconds
            self.total_seconds = self.timer_seconds
            self.render()

class TimerWidget:
    def __init__(self, parent, editor):
        self.editor = editor
        self.timer = None
        self.visible = False  # The timer is not visible by default
        self.circular_progress_bar = CircularProgressBar(parent, editor)  # Add this line

    def toggle_visibility(self):  # Add this method
        self.circular_progress_bar.toggle_visibility()  # Add this line
        if self.visible:
            self.visible = False
        else:
            self.visible = True

    def start_timer(self):
        self.circular_progress_bar.start_timer(self.circular_progress_bar.total_seconds, self.circular_progress_bar.timer_seconds)  # Add this line

    def stop_timer(self):
        self.circular_progress_bar.stop_timer()  # Stop the timer in the CircularProgressBar

    def set_timer(self):
        minutes = simpledialog.askinteger("Set Timer", "Enter the number of minutes for the timer:")
        if minutes is not None:
            self.stop_timer()
            self.circular_progress_bar.timer_seconds = minutes * 60
            self.circular_progress_bar.total_seconds = minutes * 60
            self.circular_progress_bar.render()

    def toggle_dark_mode(self):
        self.circular_progress_bar.toggle_dark_mode()

    def change_bg_color(self):
        self.circular_progress_bar.change_bg_color()

    def change_text_color(self):
        self.circular_progress_bar.change_text_color()

    def change_timer_color(self, color):
        self.circular_progress_bar.change_timer_color(color)
    
class RasaEditor:
    def __init__(self, root):
        self.rendered = False
        self.distraction_free_on = False
        self.dark_mode_on = False

        self.root = root
        self.text = tk.Text(root, font=("Dejavu Sans Mono", 12, 'bold'), insertbackground='#0f0a20', undo=True, borderwidth=0)
        self.text.config(bg='#fdfdfd', fg='#0f0a20')

        # Set the background color of the root window to be the same as the textbox
        self.root.config(bg=self.text.cget('bg'))

        # Create a grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Place the text widget in the center column of the grid with padding
        self.text.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)  # Add padding around the top, bottom, and sides

        root.bind('<Motion>', self.show_menu)

        self.menu = tk.Menu(root)  # Create a Menu widget
        root.config(menu=self.menu)  # Configure the root window to use this menu

        self.file_menu = FileMenu(self.menu, self)  # Pass the Menu widget to the FileMenu
        self.edit_menu = EditMenu(self.menu, self)  # Pass the Menu widget to the EditMenu
        self.view_menu = ViewMenu(self.menu, self)  # Pass the Menu widget to the ViewMenu
        self.timer_widget = TimerWidget(root, self)
        self.timer_menu = TimerMenu(self.menu, self.timer_widget)  # Pass the Menu widget to the TimerMenu

    def new_file(self):
        self.text.delete('1.0', tk.END)

    def open_file(self):
        file_path = filedialog.askopenfilename()
        with open(file_path, 'r') as file:
            content = file.read()
        self.text.delete('1.0', tk.END)
        self.text.insert('1.0', content)

    def save_file(self):
        file_path = filedialog.asksaveasfilename()
        if file_path == '':
            return
        with open(file_path, 'w') as file:
            content = self.text.get('1.0', 'end')
            file.write(content)

    def distraction_free(self):
        if self.distraction_free_on:
            self.root.attributes('-fullscreen', False)
            if self.menu.index('end') == 0:
                self.menu.add_cascade(label="File", menu=self.file_menu)
                self.menu.add_cascade(label="Edit", menu=self.edit_menu)
                self.menu.add_cascade(label="View", menu=self.view_menu)
                self.menu.add_cascade(label="Timer", menu=self.timer_menu)
            self.distraction_free_on = False
        else:
            self.root.attributes('-fullscreen', True)
            if self.menu.index('end') == 4:
                self.menu.delete("File")
                self.menu.delete("Edit")
                self.menu.delete("View")
                self.menu.delete("Timer")
            self.distraction_free_on = True

    def dark_mode(self):
        if self.dark_mode_on:
            self.text.config(bg='#fdfdfd', fg='#0f0a20', insertbackground='#0f0a20')
            self.root.config(bg='#fdfdfd')
            self.timer_widget.toggle_dark_mode()
            self.dark_mode_on = False
        else:
            self.text.config(bg='#0f0a20', fg='#fdfdfd', insertbackground='#fdfdfd')
            self.root.config(bg='#0f0a20')
            self.timer_widget.toggle_dark_mode()
            self.dark_mode_on = True

    def show_menu(self, event):
        if self.distraction_free_on and event.y < 1:
            if self.menu.index('end') == 0:
                self.menu.add_cascade(label="File", menu=self.file_menu.file_menu)
                self.menu.add_cascade(label="Edit", menu=self.edit_menu.edit_menu)
                self.menu.add_cascade(label="View", menu=self.view_menu.view_menu)
                self.menu.add_cascade(label="Timer", menu=self.timer_menu.timer_menu)
        elif self.distraction_free_on:
            if self.menu.index('end') == 4:
                self.menu.delete("File")
                self.menu.delete("Edit")
                self.menu.delete("View")
                self.menu.delete("Timer")

    def toggle_render_markdown(self):
        if self.rendered:
            # Configure all rows and columns to expand
            for i in range(3):
                self.root.grid_rowconfigure(i, weight=1)
                self.root.grid_columnconfigure(i, weight=1)
            self.text.grid(row=0, rowspan=3, column=1, sticky="nsew", padx=10, pady=10)  # Add padding around the top, bottom, and sides
            self.html_view.grid_forget()
            self.rendered = False
        else:
            content = self.text.get('1.0', 'end')
            html = markdown.markdown(content)
            self.html_view = HTMLScrolledText(self.root, html=html)
            # Configure all rows and columns to expand
            for i in range(3):
                self.root.grid_rowconfigure(i, weight=1)
                self.root.grid_columnconfigure(i, weight=1)
            self.html_view.grid(row=0, column=0, rowspan=3, columnspan=3, sticky="nsew")  # Adjust rowspan and columnspan
            self.text.grid_forget()
            self.rendered = True

root = tk.Tk()
if "nt" == os.name:
    root.wm_iconbitmap(bitmap = "Rasa-Logo.ico")
else:
    root.wm_iconbitmap(bitmap = "@Rasa-Logo.xbm")
root.title("Rasa")
app = RasaEditor(root)
root.mainloop()
