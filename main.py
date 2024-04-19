from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import pickle
from os import path as ospath
from random import randint

"""
COMP.CS.100 Ohjelmointi 1.
Magnus Forsblom, magnus.forsblom@tuni.fi
13.10 Projekti: Graafinen käyttöliittymä
MyCookBook - A solution for all your cookbook needs
Note to assistant: The project aims to be an advanced GUI.

Features:
MyCookBook has many features. It allows you to store your cooking recipes
digitally in a virtual cookbook. You can add as many recipes as you want, and
they will automatically be saved and loaded back when you restart the program.
You can create a new recipe by clicking the "Add" Button in the Main UI. To
Create a recipe you need to enter a name, (optional description) and some
ingredients for the recip.e You can also create new cookbooks, for example for
different kinds of recipes. It is also possible to load cookbooks that you or
others have created from file with the easy load feature. If you wish to export
your own cookbook it is easy with the Export cookbook feature, where you can
choose between MyCookBooks own cookbook format (For my cookbook), or a standard
human-readable .txt file.

Besides these basic cookbook features, MyCookBook has many more recipe related
functions. You can create, edit and remove recipes from your cookbook with
ease. It is also possible to view them with the easy recipe viewer that is
built in to the program. Just double click any recipe from the recipes listbox,
or click the view button to view the selected recipe. Furthermore, it is also
possible to search for recipes from your cookbooks with the Find feature. You
can choose to search for recipe names, recipe ingredients or both. If you just
want to quickly find a certain recipe, the sorting system can help you out.
With just two clicks, you can change the recipe sorting order between
First added, last added, A-Z and Z-A.

How does the app work?
MyCookBook tries to load the cookbook file location from a config file
MyCookBook.config that is located the same directory
where this (main.py) file is located in. If successfull, the recipe file
will be loaded from the file location that is stored in the config file.
If MyCookBook.config is not found, MyCookBook assumes that a first time
startup has occurred, and displays a welcome message. As default, a cookbook
with the name recipes.cookbook is created in the app directory
(same directory as main.py). You are free to create your own cookbook in a
location you desire with the above mentioned create recipe function.

When closing, or loading an other cookbook, the current recipes are saved to
the above mentioned cookbook location (loaded from the config file, or default
recipes.cookbook). The recipes are save with pickle to a .cookbook file. Pickle
protocol 4 has been used to ensure future backwards compatibility  down to
python 3.4 (but other parts of this app require at least python 3.6)

PLEASE NOTE
!!!
When loading cookbooks, it is important to only load cookbooks from trusted
places. The creator of this program is not responsible for code execution
that can occur with pickle when loading unsafe cookbooks!
!!!

Requirements:
Python version 3.6 or greater
Tested on Windows 10 and Linux Mint

How to run?
Place MyCookBook (main.py) in a suitable location on your computer, where it
has read and write access to the folder it is stored in. This is to allow
MyCookBook to store required files (config file and possibly default cookbook
file)
Execute MyCookBook by running main.py (this file)
"""

# Initialize global constant variables
# used for the UI

# used globally in the app
BIG_FONT = "Arial 16"
BUTTON_FONT = "Arial 11"

# used in the main window button placement
BUTTON_WIDTH = "25"
BUTTON_HEIGHT = "2"

# used in the main window button placement
BUTTON_X_PAD = 5
BUTTON_Y_PAD = 5


class Recipe:

    def __init__(self, name, description, ingredients, index):
        """
        Initalize the Recipe object, used to store recipe information
        including recipe name, description and ingredients.
        :param name: str, the name of the recipe
        :param description: str, the description for the recipe
        :param ingredients: str, the ingredients for the recipe
        :param index: int, the recipe index (each recipe gets its own index)
        """
        # initialize recipe str: recipe name, description and ingredients
        self.__recipe_name = name.rstrip()
        self.__recipe_description = description.rstrip()
        self.__recipe_ingredients = ingredients.rstrip()

        # set index on creation, used for sorting
        self.__index = index

    def get_ingredients(self):
        """
        Gets the recipe ingredients.
        :return: str, recipe ingredients
        """
        return self.__recipe_ingredients

    def get_description(self):
        """
        Gets the recipe description.
        :return: str, recipe description
        """
        return self.__recipe_description

    def get_name(self):
        """
        Gets the recipe name.
        :return: str, recipe name
        """
        return self.__recipe_name

    def get_index(self):
        """
        Gets the recipe index.
        :return: int, recipe index
        """
        return self.__index

    def decrement_index(self):
        """
        Decrements the recipe index value with one int.
        :return: None
        """
        self.__index -= 1


class MainWindow:

    def __init__(self):
        """
        Initializes the MainWindow tkinter window that is used as the main
        communications channel to control different functions in the app.
        All the main features (widgets) are placed by grid geometry manager
        on this main window.
        :return: None
        """
        # This is the main window where all main program events are handled

        # set default cookbook location, used if no other value is specified
        self.__cb_file_location = "recipes.cookbook"

        # variable to store if opened cookbook is new default
        # default  value is false, because no new cookbook has been loaded
        self.__is_new_default = False

        # Initialize Recipe list
        self.__recipes_list = []

        # initalize recipe list sort type (value of self.__combobox_sort_type)
        self.__sort_type = 0

        # initialize selected_index
        self.__selected_index = None

        # set biggest index in the list, at first there are no items in the
        # list so the value is -1
        self.__biggest_index = -1

        # create main window tk object
        self.__main = Tk()

        # set the window size
        self.__main.minsize(width=650, height=600)

        # set window title
        self.__main.title("MyCookBook")

        # Create frames for UI
        self.__frame_listbox = Frame(self.__main, background="white")
        self.__frame_actions = Frame(self.__main, background="white")

        # Create widgets for the UI
        self.__label_cookbook_name = Label(self.__frame_listbox,
            text="Recipes:", font=BIG_FONT, background="white")
        self.__combobox_sort_type = ttk.Combobox(self.__frame_listbox,
            values=("First added", "Last added", "A-Z", "Z-A"),
            state="readonly", font=BUTTON_FONT)
        self.__listbox_recipe_list = Listbox(self.__frame_listbox,
            font=BIG_FONT)
        self.__label_actions = Label(self.__frame_actions, text="Actions:",
            font=BIG_FONT, background="white")
        self.__button_view = Button(self.__frame_actions,
            command=self.open_view_recipe, text="View",
            font=BUTTON_FONT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        self.__button_add = Button(self.__frame_actions,
            command=self.open_add_recipe, text="Add",
            font=BUTTON_FONT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        self.__button_remove = Button(self.__frame_actions,
            command=self.ask_remove_recipe, text="Remove", font=BUTTON_FONT,
            width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        self.__button_edit = Button(self.__frame_actions, text="Edit",
            command=self.open_edit_recipe, font=BUTTON_FONT,
            width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        self.__label_tools = Label(self.__frame_actions, text="Tools:",
            font=BIG_FONT, background="white")
        self.__button_find = Button(self.__frame_actions,
            command=self.open_find_recipe, text="Find", font=BUTTON_FONT,
            width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        # lambda is used because it allows function arguments to be passed
        # in the command field without immediately executing the function
        self.__button_new_cb = Button(self.__frame_actions,
            command=lambda: self.open_general_load_action("new"),
            text="New cookbook", font=BUTTON_FONT, width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT)
        self.__button_load_cb = Button(self.__frame_actions,
            command=lambda: self.open_general_load_action("load"),
            text="Load cookbook", font=BUTTON_FONT, width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT)
        self.__button_export_cb = Button(self.__frame_actions,
            command=lambda: self.open_general_load_action("export"),
            text="Export cookbook",
            font=BUTTON_FONT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)

        # place the widgets in correct position with tkinter grid
        # There are two frames self.__frame_listbox on the left and
        # self.__frame_actions on the left. The listbox frame contains
        #  self.__label_cookbook_name "Recipes" label and below it
        # and the self.__combobox_sort_type that is used to select the
        # sort order of the recipes. Below them is the
        # self.__listbox_recipe_list listbox where all the recipe objects
        # will be loaded. On the left side the self.__frame_actions contains
        # all the main actions (buttons for add, remove, edit etc..)
        self.__label_cookbook_name.grid(sticky="W", column=0, row=0, padx=5,
                                        pady=2)
        self.__listbox_recipe_list.grid(sticky="NWSE", column=0, row=1, padx=2,
                                        pady=2, columnspan=2)
        self.__combobox_sort_type.grid(sticky="E", column=1, row=0, padx=2,
                                       pady=2)
        self.__label_actions.grid(sticky="NW", column=0, row=0, padx=5, pady=2)
        self.__button_view.grid(sticky="NW", column=0, row=1,
                                padx=BUTTON_X_PAD,
                                pady=BUTTON_Y_PAD)
        self.__button_add.grid(sticky="NW", column=0, row=2, padx=BUTTON_X_PAD,
                               pady=BUTTON_Y_PAD)
        self.__button_remove.grid(sticky="NW", column=0, row=3,
                                  padx=BUTTON_X_PAD, pady=BUTTON_Y_PAD)
        self.__button_edit.grid(sticky="NW", column=0, row=4,
                                padx=BUTTON_X_PAD, pady=BUTTON_Y_PAD)
        self.__button_find.grid(sticky="NW", column=0, row=5,
                                padx=BUTTON_X_PAD, pady=BUTTON_Y_PAD)
        self.__label_tools.grid(sticky="NW", column=0, row=6, padx=5, pady=5)
        self.__button_new_cb.grid(sticky="NW", column=0, row=7,
                                  padx=BUTTON_X_PAD, pady=BUTTON_Y_PAD)
        self.__button_load_cb.grid(sticky="NW", column=0, row=8,
                                   padx=BUTTON_X_PAD, pady=BUTTON_Y_PAD)
        self.__button_export_cb.grid(sticky="NW", column=0, row=9,
                                     padx=BUTTON_X_PAD, pady=BUTTON_Y_PAD)

        self.__frame_listbox.grid(column=0, row=0, sticky="NWSE")
        self.__frame_actions.grid(column=1, row=0, sticky="NWSE")

        # configure columns and rows, we want the widgets to scale when the app
        # is resized
        self.__main.columnconfigure(0, weight=1)
        self.__main.rowconfigure(0, weight=1)
        self.__frame_listbox.columnconfigure(0, weight=1)
        self.__frame_listbox.rowconfigure(1, weight=1)

        # set sorting combobox value to default "First added"
        self.__combobox_sort_type.set("First added")

        # bind event to combobox when item selection is changed
        self.__combobox_sort_type.bind("<<ComboboxSelected>>",
                                       self.combobox_index_changed_event)

        # bind events for recipes listbox: item double click and changed index
        self.__listbox_recipe_list.bind("<Double-Button>",
                                        self.listbox_double_click_event)
        self.__listbox_recipe_list.bind("<<ListboxSelect>>",
                                        self.listbox_index_changed_event)

        # bind custom close function to close event
        # (User clicks window close button)
        self.__main.protocol("WM_DELETE_WINDOW", self.window_close_event)

        # try to load cookbook location file
        if self.load_recipe_file_location():
            # if loading of cookbook location was successfull, try to load
            # recipes from it
            self.load_recipes(self.__cb_file_location)

        # set new title
        self.__main.title(f"MyCookBook - {self.__cb_file_location}")

        # start the window loop
        self.__main.mainloop()

    def open_view_recipe(self):
        """
        Opens ViewRecipeWindow() tkinter window that is used to view
        Recipe object details. Passes on selected recipe as a parameter.
        :return: None
        """

        # check if a valid recipe is selected
        if self.is_recipe_selected():

            # get the selected recipe
            recipe = self.get_selected_recipe()

            # initialize ViewRecipeWindow, pass on the recipe to view
            # as an argument
            view_recipe_window = ViewRecipeWindow(self.__main, self, recipe)
            # change focus to ViewRecipeWindow
            view_recipe_window.grab_set()
            # stop listening for events on MainWindow (make it inactive)
            self.__main.wait_window(view_recipe_window)

    def open_add_recipe(self):
        """
        Opens EditRecipeWindow() tkinter window in new recipe mode. The
        window is used to get new recipe details to be added to the recipes
        list.
        :return: None
        """
        # initialize EditRecipeWindow, when no argument is passed, the default
        # is add, the EditRecipeWindow opens in "add recipe" mode
        add_recipe_window = EditRecipeWindow(self.__main, self)
        # grab focus
        add_recipe_window.grab_set()
        # stop listening for events on MainWindow (make it inactive)
        self.__main.wait_window(add_recipe_window)

    def open_edit_recipe(self):
        """
        Opens EditRecipeWindow() tkinter window that is used to edit selected
        recipe details. Gets selected recipe with get_selected_recipe()
        function that is passed to EditRecipeWindow() to be processed.
        :return: None
        """
        # Check if a recipe is currently selected from the recipes listbox
        if self.is_recipe_selected():
            # get the selected recipe
            selected_recipe = self.get_selected_recipe()
            # initialize EditRecipeWindow, pass on the recipe to view
            # as an argument
            edit_recipe_window = EditRecipeWindow(self.__main, self, "edit",
                                                  selected_recipe)
            # grab focus
            edit_recipe_window.grab_set()
            # stop listening for events on MainWindow (make it inactive)
            self.__main.wait_window(edit_recipe_window)

        # If no recipe selected, do nothing

    def ask_remove_recipe(self):
        """
        Gets selected recipe. If a valid recipe is selected asks user if that
        recipe shall be deleted. Performs actions accordingly. If recipe shall
        be deleted it will be removed from the recipes list. if not, no action
        will be performed.
        :return: None
        """
        # check if a recipe has been selected
        if self.is_recipe_selected():
            # get selected recipe
            selected_recipe = self.get_selected_recipe()

            # get selected recipe name
            recipe_name = selected_recipe.get_name()

            # show messagebox and save answer
            answer = messagebox.askyesno("Delete recipe?",
                    f"Are you sure you want to permanently delete\n"
                    f"the recipe for {recipe_name}?")

            # check if answer is true
            if answer is True:
                # user wants to delete recipe:
                # Delete recipe
                self.__recipes_list.pop(self.__selected_index)
                # decrement index for all recipe objects that have bigger
                # index than self.__selected_index
                self.update_recipes_index(selected_recipe.get_index())
                self.__biggest_index -= 1
                self.refresh_recipe_listbox()

            # If answer not True (yes), do nothing

    def open_find_recipe(self):
        """
        Opens the FindRecipeWindow tkinter window that is used to search
        for recipe names and ingredients.
        :return: None
        """
        # Initialize FindRecipeWindow
        find_recipe_window = FindRecipeWindow(self.__main, self)
        # grab focus
        find_recipe_window.grab_set()
        # stop listening for events on MainWindow (make it inactive)
        self.__main.wait_window(find_recipe_window)

    def open_general_load_action(self, mode):
        """
        Opens GeneralActionWindow tkinter window that in specified mode. There
        are 3 different modes that change the UI and function of the
        GeneralActionWindow.
        mode:
        1) "save" = UI and function to create new recipe
        (Create new recipe button)
        2) "load" UI and function to load a cookbook file (Load recipe button)
        3) "export" UI and function to export cookbook file (Export recipe
        button)
        :param mode: str, what mode to open the window in
        :return: None
        """
        # Initialize GeneralActionWindow, set mode according to mode
        # parameter
        export_cb_window = GeneralActionWindow(self.__main, self, mode=mode)
        # set focus to GeneralActionWindow
        export_cb_window.grab_set()
        # stop listening for events on MainWindow (make it inactive)
        self.__main.wait_window(export_cb_window)

    def add_recipe(self, recipe):
        """
        Adds param=Recipe object to recipes list and refreshes visual recipe
        listbox.
        :param recipe: object, Recipe to be added to recipe list.
        :return: None
        """
        # add recipe object to recipes list
        self.__recipes_list.append(recipe)

        # refresh listbox
        self.refresh_recipe_listbox()

    def save_edit(self, recipe):
        """
        Saves the new recipe details that have been edited in
        EditRecipeWindow() to the correct index in recipe list for the edited
        recipe and refreshes visual recipe listbox.
        :param recipe: object, edited Recipe object.
        :return: None
        """

        # save edited recipe object to correct index in recipes list
        self.__recipes_list[self.__selected_index] = recipe

        # refresh recipe list
        self.refresh_recipe_listbox()

    def create_new_cookbook(self, path):
        """
        Creates a new cookbook file in desired path. Zeroes all cookbook
        related values to default.
        :param path: str, file path where the cookbook will be stored
        :return: None
        """
        # set required values for new cookbook
        # clear recipes list
        self.__cb_file_location = path
        self.__is_new_default = True
        self.__biggest_index = -1
        self.__recipes_list = []
        self.refresh_recipe_listbox()

    def export_cookbook_to_file(self, path, file_type):
        """
        Exports the cookbook to desired path in desired format. Format will
        depend on user selection (.txt or .cookbook file)
        :param path: str, the file path where the cookbook will be exported to.
        :param file_type: int, type of exported file (0=.txt; 1=.cookbook)
        :return: None
        """
        # add export filename to path, randomly created
        path += f"/EXPORTED_COOKBOOK{randint(0, 9999)}"

        # as cookbook file (for use with MyCookBook app)
        if file_type == 1:
            # add .cookbook file ending
            path += ".cookbook"
            # open file in write bytes mode
            file = open(path, "wb")
            # use pickle to dump recipe list to file, protocol=4 to guarantee
            # backwards compatibility for python versions >= 3.4
            pickle.dump(self.__recipes_list, file, protocol=4)

        # as txt file (human-readable)
        elif file_type == 0:
            # add .txt file ending
            path += ".txt"
            file = open(path, "w")

            # loop through all recipes in recipes list
            for recipe in self.__recipes_list:
                # write recipe information to txt file
                file.write(f"Recipe name: {recipe.get_name()}\n"
                           f"Description:\n{recipe.get_description()}\n"
                           f"Ingredients:\n{recipe.get_ingredients()}\n\n")

        # show export success message
        messagebox.showinfo(title="Export success!",
                message=f"Successfully exported cookbook as: {path}")

    def find_recipe(self, search_string, search_option):
        """
        Function to search if specified <search_string> is found from
        all the recipe objest names or ingredients in the recipes list.
        search_option specifies if recipe name, ingredients or both should
        be searched. If search string is found in the recipe objects, the
        specified index in the visual listbox will be colored green.
        A message will also be displayed to the user telling about the
        search status.

        1) search_option=1 Search recipe name
        2) search_option=1 Search recipe ingredients
        3) search option=3 Search recipe name and ingredients

        :param search_string: str, the string to search from recipe object
        name and ingredients
        :param search_option: int, the option that specifies what should be
        searched (recipe name, ingredients or both)
        :return: None
        """

        # initialize flag for found search result, default false because no
        # search has been done
        search_string_found = False

        # iterate trough recipes list and increment index i for each iteration
        for i, recipe in enumerate(self.__recipes_list):
            # check if recipe name should be searched (either 1, only name, or
            # 3, both name and ingredients
            if search_option in (1, 3):
                # check if search string is in lowercase recipe name
                if search_string in recipe.get_name().lower():
                    # set the matching recipe item background to green in the
                    # recipes listbox
                    self.__listbox_recipe_list.itemconfig(i, bg="green")
                    # set search success flag as true
                    search_string_found = True
            # check if recipe ingredients should be searched (either 1, only
            # ingredients, or 3, both name and ingredients
            if search_option in (2, 3):
                # check if search string is in lowercase recipe ingredients
                if search_string in recipe.get_ingredients().lower():
                    # set the matching recipe item background to green in the
                    # recipes listbox
                    self.__listbox_recipe_list.itemconfig(i, bg="green")
                    # set search success flag as true
                    search_string_found = True

        # if search string matches:
        if search_string_found:
            # results found, show message
            messagebox.showinfo(title="Search results:",
            message=f"Matching recipes for search string: {search_string}"
            "\nhave been marked with green.")
        else:
            # no results, show message
            messagebox.showinfo("Search results:",
            message=f"No recipes matched {search_string}")

    def refresh_recipe_listbox(self):
        """
        Sorts recipes with sort function according to user selection.
        Refreshes all recipe objects from recipe list to visual listbox
        in the correct order.
        :return: None
        """

        # when refreshing list set selected recipe to None
        self.__selected_index = None

        # sort the list according to sort type
        self.sort_recipes(self.__sort_type)

        # clear the listbox of items
        self.__listbox_recipe_list.delete(0, END)

        # fill the listbox with items
        for i in range(len(self.__recipes_list)):

            # insert recipe from recipes list to listbox
            self.__listbox_recipe_list.insert(i, self.__recipes_list[
                i].get_name())

            # get the index of current recipe
            creation_index = self.__recipes_list[i].get_index()

            # USED FOR SORTING:
            # compare if current recipe index is bigger than biggest index
            # stored
            if creation_index > self.__biggest_index:
                # if so, set new biggest index as current recipe index
                self.__biggest_index = creation_index

    def sort_recipes(self, sort_type=0):
        """
        Sorts recipes in recipes list according to param <sort_type>. There are
        4 different sort types. Updates the recipes list with the new sorted
        order.

        1 )sort_type == 0 Sorts the recipes in recipes list from first added
        to last added. Loops trough every recipe object in recipe list and gets
        the recipes index with. recipe.get_index(). In the end all recipes will
        be sorted from smallest to biggest index.

        2) elif sort_type == 1 Sorts the recipes in recipes list from last
        added to first added. Loops trough every recipe object in recipe list
        and gets the recipes index with. recipe.get_index(). In the end all
        recipes will be sorted from biggest to smallest index.

        3) sort_type == 2 Sorts the recipes in recipes list by name from A-Z.
        Loops trough every recipe object in recipe list and gets the recipes
        name with recipe.get_name(). The comparison is done with pythons built
        in sorting method (< and >) operators. In the end all recipes will be
        sorted from smallest char to biggest char.

        4) sort_type == 3 Sorts the recipes in recipes list by name from Z-A.
        Loops trough every recipe object in recipe list and gets the recipes
        name with recipe.get_name(). The comparison is done with pythons built
        in sorting method (< and >) operators. In the end all recipes will be
        sorted from biggest char to smallest char.

        :param sort_type: int, the sorting method (0-3)
        :return: None
        """
        # create empty list, will store the recipe objects in new sorted order
        sorted_order = []

        # sort_type:
        # lambda is used to access the recipe object and its functions.
        # First added
        if sort_type == 0:
            sorted_order = sorted(self.__recipes_list,
                                 key=lambda recipe: recipe.get_index())

        # last added
        # same as sort_type=0 but reverse the order with reverse=True
        # param
        elif sort_type == 1:
            sorted_order = sorted(self.__recipes_list,
                                 key=lambda recipe: recipe.get_index(),
                                 reverse=True)
        # a-z
        elif sort_type == 2:
            sorted_order = sorted(self.__recipes_list,
                                 key=lambda recipe:
                                 recipe.get_name().lower())
        # z-a
        # same as sort_type=2 but reverse the order with reverse=True
        elif sort_type == 3:
            sorted_order = sorted(self.__recipes_list,
                                 key=lambda recipe:
                                 recipe.get_name().lower(),
                                 reverse=True)

        # set the sorted order_list as the new recipes list
        self.__recipes_list = sorted_order

    def update_recipes_index(self, deleted_recipe_index):
        """
        Updates the indexes for all the Recipe objects in recipes list that
        have a bigger index than the index of the recipe that was deleted,
        in order to keep correct index order of the list.

        Eg. Recipes amount in recipes list: 3 (indexes 0,1,2).
        Deleted recipe index: 1
        Updates recipe with index 2 --> index 1. And new index order is 0,1
        :param deleted_recipe_index: int, index of deleted recipe
        :return: None
        """
        # loop trough all the recipes
        for recipe in self.__recipes_list:
            # if recipe index is bigger than deleted_recipe_index: decrement
            # recipe index by -1
            if recipe.get_index() > deleted_recipe_index:
                # decrements recipe index by -1
                recipe.decrement_index()

    def save_recipes(self):
        """
        Saves all the recipes from recipes list to desired file using pickle.
        File path is set with global variable self.__recipe_file_location (str)

        If opened cookbook is new_default=True (shall be set to be opened on
        starup, will write cookbook path to config file MyCookBook.config.
        :return: None
        """
        # save recipes to file recipe file location
        try:
            file = open(self.__cb_file_location, "wb")
        except FileNotFoundError:
            # file save failed, with all the security measures, this error
            # should not really be possible, but a fail-safe is still good

            # get the location that saving was not possible to
            invalid_loc = self.__cb_file_location

            # set panic save location
            self.__cb_file_location = "PANIC_SAVE.cookbook"

            # save new panic save location to config, so that the error
            # will not repeat itself
            self.__is_new_default = True

            # recipes will be saved to new location
            file = open(self.__cb_file_location, "wb")

            # display messsage to user informing about the situation
            messagebox.showwarning(title="Save error!",
                message=f"The file {invalid_loc} can not be found. Your"
                        f" current cookbook has been saved in"
                        f" the app directory with name PANIC_SAVE.cookbook")
            # continue with saving process:

        # use pickle to dump all the objects in recipe list to file.
        # pickle is used because it is easy to use and the program does not
        # need human-readable files, we also assume that the user only uses
        # local trusted files (because pickle is vulnerable to code execution)
        # protocol=4 to guarantee backwards compatibility for python versions
        # >= 3.4
        pickle.dump(self.__recipes_list, file, protocol=4)

        # check if currently opened cookbook is to be set as new default
        # (opened always on startup)
        if self.__is_new_default:
            # if that is the case, save new cookbook location to config file
            file = open("MyCookBook.config", "wb")
            # dump string to file with pickle, protocol=4 for backwards
            # compatibility
            pickle.dump(self.__cb_file_location, file, protocol=4)

    def load_recipe_file_location(self):
        """
        Tries to load cookbook file location from config file
        MyCookBook.config. If config file is not found, it is assumed that
        the user is starting the app for the first time, and first_startup()
        function is executed to handle all necessary actions related to that.
        :return: None
        """
        # try to load config file, that contains location for the cookbook
        try:
            file = open("MyCookBook.config", "rb")
            # set cookbook file location
            self.__cb_file_location = pickle.load(file)

            # loading of config file was successfull
            return True

        except FileNotFoundError:
            # the config file is not found, assume first startup
            self.first_startup()

            # loading of config file was not successfull, return False
            return False

    def load_recipes(self, filename, is_default=False):
        """
        Tries to load recipes from specified filename (path) to recipes list
        with pickle. Accepts bool param=is_default that dictates if the
        default location for cookbook location should be changed to the
        current param <filename> that is being loaded. Default for
        param <is_default> is False.
        Returns true if loading is successfull, and False if not.
        :param filename: str, the path for the cookbook file that is to be
        loaded
        :param is_default: bool, is the file being loaded new_default, that is
        to be always loade on startup. Default value is_default=False
        :return:
        """

        # try to load recipes from specified cookbook file
        try:
            # open file with in read bytes mode (rb) for pickle
            file = open(filename, "rb")
        except FileNotFoundError:
            # file not found
            # create new recipes file for user
            self.__cb_file_location = f"recipes{randint(1,9999)}.cookbook"
            # set new recipe file to be the default
            self.__is_new_default = True

            # show message to user
            messagebox.showinfo(title="Failed to load cookbook!",
                message=f"The specified cookbook to load: {filename}"
                        f" was not found! Your current cookbook will be saved"
                        f" to {self.__cb_file_location} in the app directory"
                        f" if you do not manually create or load a cookbook.")
            return False

        try:
            # load recipes to recipes listfrom cookbook file
            self.__recipes_list = pickle.load(file)

            # set recipes location to cookbook path
            self.__cb_file_location = filename

            # check if the loaded cookbook file is to be set as new default
            if is_default:
                # set self.__is_new_default flag as True
                self.__is_new_default = True

            # set recipes biggest index to -1 after loading and refresh list
            self.__biggest_index = -1
            self.refresh_recipe_listbox()

            # append file path to MainWindow title
            self.__main.title(f"MyCookBook - {self.__cb_file_location}")

            # Return true, loading success
            return True
        except Exception:
            # Error while loading cookbook file. Broad exception, because many
            # types of errors can happen while reading cookbook file, and
            # catching them all in this case would be pointless. This function
            # is only run on startup, so a broad exception clause does not
            # mess up the behaviour of the app otherwise.
            # Return False, loading recipes failed
            return False

    def get_listbox_selection(self):
        """
        Tries to get the selected index from listbox. Returns selected index.
        If no valid index is selected, returns None.
        :return: int or None, returns selected index.
        """
        # try to get recipes listbox index selection
        try:
            # valid index, return the selected index
            return self.__listbox_recipe_list.curselection()[0]
        except IndexError:
            # nor valid index, return None as the new selected index
            return None
            pass

    def get_selected_recipe(self):
        """
        Gets the currently selected recipe from the visual listbox. Returns
        the selected recipe object. If no valid recipe is selected, the
        function does nothing
        :return:
        """

        # check if selected index is valid (not None)
        if self.__selected_index is not None:
            # return the recipe object that corresponds to the selected index
            return self.__recipes_list[self.get_listbox_selection()]

        # If not valid index, do nothing

    def is_recipe_selected(self):
        """
        Checks if a recipe is selected in the recipes listbox. Performs the
        check by getting the currently selected index from the listbox with
        get_listbox_selection() function. If a valid index is selected returns
        True, else returns False
        :return: None
        """

        # check if a valid item has been selected from recipes listbox
        if self.get_listbox_selection() is not None:
            # if that is the case, return true
            return True

        # Else no recipe selcted, display error
        messagebox.showinfo(title="No recipe selected!",
                            message="No recipe selected. Please select a"
                                    " recipe from\nthe recipes listbox first.")
        # return False
        return False

    def window_close_event(self):
        """
        Function for tkinter window close event (X-button is pressed etc.)
        Saves all recipes with save_recipes() before closing main window and
        quitting app.
        :return: None.
        """
        # when application is closing recipes will be saved
        self.save_recipes()

        # close the main window, exit app
        self.__main.destroy()

    def listbox_double_click_event(self, event):
        """
        Function that is called when an item in the visual recipes listbox
        is double-clicked with mouse button. Calls open_view_recipe()
        :param event: tkinter event, click event.
        :return: None
        """
        # this function is evoked when an item in listbox is doubleclicked
        # This means that the currently selected item in listbox should
        # be opened
        self.open_view_recipe()

    def listbox_index_changed_event(self, event):
        """
        Function that is called when the index of the listbox changes. Calls
        get_listbox_selection() to get the new index. If new index is a valid
        self.__selected_index will be updated to new index. If new index is
        None (not a valid index) nothing will be done.
        :param event: tkinter event, index changed event.
        :return:
        """
        # get the new index
        index = self.get_listbox_selection()

        if index is not None:
            # if index is valid, update self.__selected_index to new index
            self.__selected_index = index

    def combobox_index_changed_event(self, event):
        """
        Funtion that is called when the index of combobox changes. Sets
        self.__sort_type according to combobox selection. Refreshes visual
        recipes listbox to update the new sorting order visually.
        :param event: tkinter event, index changed event.
        :return:
        """
        # get selected index from sort type combobox
        self.__sort_type = self.__combobox_sort_type.current()

        # refresh listbox, also sorts the listbox with new sort type
        self.refresh_recipe_listbox()

    def get_biggest_index(self):
        """
        Gets the biggest recipe object index that is currently in the
        recipes list.
        :return: int, biggest recipe object index in recipes list
        """
        return self.__biggest_index

    def first_startup(self):
        """
        Function is run when first starup is detected (failed to load cookbook
        location config file). Displays a welocme message to user.
        :return: None
        """

        # set empty cookbook as default
        self.__is_new_default = True

        # show welcome message
        messagebox.showinfo(title="Welcome!", message="Welcome to MyCookBook\n"
        "To get started you can add your favourite recipes by clicking the Add"
        " button on the right. If you already have an existing cookbook"
        ", you can load it by selecting Load Cookbook from the bottom right"
        " corner.")


class FindRecipeWindow(Toplevel):
    def __init__(self, parent, root):
        """
        Initialize FindRecipeWindow window object as a new TopLevel tkinter
        window that inherits from parent MainWindow(). This window is used to
        search for search string from recipe object names and ingredients.
        :param parent: tkinter.tkapp, the parent GUI.
        :param root: MainWindow object, allow access and communication
        to all MainWindow functions from FindRecipeWindow
        """
        # Inherit from MainWindow with super()
        super().__init__()

        # set root_window as the "communications channel" for MainWindow
        # functions and methods
        self.root_window = root

        # prevent window from being resized
        self.resizable(0, 0)

        # initialize values
        self.__search_recipes = BooleanVar()
        self.__search_ingredients = BooleanVar()

        # create tkinter widgets
        self.__label_search = Label(self, text="Search string:", font=BIG_FONT)
        self.__entry_search_string = Entry(self, font=BIG_FONT, width=20)
        self.__label_search_options = Label(self, text="Search in:",
                                        font=BUTTON_FONT)
        self.__checkbutton_name = Checkbutton(self,
                                        text="Recipe names",
                                        variable=self.__search_recipes,
                                        onvalue=True, offvalue=False)
        self.__checkbutton_ingredients = Checkbutton(self,
                                        text="Recipe ingredients",
                                        variable=self.__search_ingredients,
                                        onvalue=True,
                                        offvalue=False)
        self.__button_find = Button(self, command=self.process_search,
                                        text="Find!", font=BUTTON_FONT)

        # place widgets in correct position with pack
        self.__label_search.pack(anchor="w")
        self.__entry_search_string.pack(anchor="w", fill="x")
        self.__label_search_options.pack(anchor="w")
        self.__checkbutton_name.pack(anchor="w")
        self.__checkbutton_ingredients.pack(anchor="w")
        self.__button_find.pack(anchor="e", padx=2, pady=5)

    def process_search(self):
        """
        Processes the search string and selected search options. Checks
        that the search string is not empty, and that valid search options have
        been selected. Search string can be searched from recipe object:
        1) name
        2) ingredients
        3) name and ingredients
        This action is controlled by selecting the checkboxes in the GUI.

        Displays an error messagebox if incorrect selections have been made, or
        the search string is empty.
        :return: None
        """

        # get the search string from tkinte Entry textbox
        search_string = self.__entry_search_string.get().lower()

        # initialize erromessage as empty str
        errormessage = ""

        # initialize search option as 0, no selection
        search_option = 0

        # set search options depending on what checkbuttons have been selected
        # get selection for if recipe names should be searched
        if self.__search_recipes.get():
            # search ingredients have been selected
            search_option = 1
        # get selection for if recipe ingredients should be searched
        if self.__search_ingredients.get():
            # check if we do not search for recipe name
            if search_option != 1:
                # set search option as 2, only search for ingredients
                search_option += 2
            else:
                # should search for recipe name and ingredients, set search
                # option as 3
                search_option = 3

        # check  if search string is empty
        if search_string == "":
            errormessage += "Search string can not be empty.\n"
        # check if no valid search option has been selected (neither search
        # recipe name or ingredients)
        if search_option == 0:
            errormessage += "Search selection can not be empty."

        # check if error message is not empty
        if errormessage != "":
            # if not empty, errors, display error message
            messagebox.showinfo(title="Invalid input!", message=errormessage)
        else:
            # no errors, do search
            self.root_window.find_recipe(search_string, search_option)

            # close window after search
            self.destroy()


class GeneralActionWindow(Toplevel):
    def __init__(self, parent, root, mode):
        """
        Initializes the GeneralActionWindow as a new TopLevel tkinter
        window that inherits from parent MainWindow(). This window has many
        different functions depending on the <mode> parameter.
        GeneralActionWindow can be used to save, load, and export cookbooks.
        The <mode> parameters changes the appeareance and GUI of the
        GeneralActionWindow.
        Modes:
        1) mode="new" Create new cookbook
        2) mode="load" Load cookbook from file
        3) mode="export" Export cookbook to file in desired format (.txt or
        ".cookbook file depending on user selection)

        :param parent: tkinter.tkapp, the parent GUI.
        :param root: MainWindow object, allow access and communication
        to all MainWindow functions from FindRecipeWindow
        :param mode: str, determines what mode the GeneralActionWindow is
        loaded in.
        """

        # Inherit from MainWindow with super()
        super().__init__()

        # set root_window as the "communications channel" for MainWindow
        # functions and methods
        self.root_window = root

        # create variable for export selction (external or internal)
        self.__export_choice = IntVar()

        # variable for checkbutton, determines if loaded cookbook should be set
        # as default
        self.__default_cookbook = BooleanVar()

        # create file location variable for saving and loading cookbook
        self.__cb_location = StringVar()

        # prevent window from being resized
        self.resizable(0, 0)

        # create tkinter widgets
        self.__label_select_file_location = Label(self, font=BIG_FONT)
        self.__entry_file_location = Entry(self,
            textvariable=self.__cb_location, font=BIG_FONT)
        self.__button_browse_location = Button(self, text="...", font=BIG_FONT)
        self.__checkbutton_default_load = Checkbutton(self,
            text="Load this cookbook on startup",
            variable=self.__default_cookbook, font=BUTTON_FONT)
        self.__label_select_export_type = Label(self,
            text="How would you like to\nexport the cookbook?", font=BIG_FONT)
        self.__radiobutton_export_external = Radiobutton(self,
            text="Text file (for external use)", variable=self.__export_choice,
            value=0, font=BUTTON_FONT)
        self.__radiobutton_export_internal = Radiobutton(self,
            text="Cookbook file (For MyCookBook)",
            variable=self.__export_choice, value=1, font=BUTTON_FONT)
        self.__button_do_action = Button(self, padx=2, pady=2)
        self.__button_cancel = Button(self, text="Cancel",
            command=self.destroy, padx=2, pady=2)

        # place widgets to correct position with grid
        self.__label_select_file_location.grid(column=0, row=0, sticky="W")
        self.__entry_file_location.grid(column=0, row=1, sticky="WE")
        self.__button_browse_location.grid(column=1, row=1, sticky="W")

        # place more widgets according to what mode is selected
        if mode == "new":
            # New cookbook mode, place widgets to create new cookbook and
            # configure correct button and text for labels
            self.title("MyCookBook - New CookBook")

            # config functions for widgets
            self.__label_select_file_location.config(text="Location to store "
                                                          "new cookbook in:")
            self.__button_browse_location.config(
                command=lambda: self.browse_file("save"))
            self.__button_do_action.config(text="Create",
                command=self.create_new_cookbook)

        elif mode == "load":
            # Load cookbook mode, place widgets to load existing cookbook from
            # file and configure correct button functions and text for labels
            self.title("MyCookBook - Load CookBook")

            # config functions for widgets
            self.__label_select_file_location.config(text="Cookbook location:")
            self.__button_browse_location.config(
                command=lambda: self.browse_file("load"))

            # place widgets with grid
            self.__checkbutton_default_load.grid(column=0, row=2, sticky="w")
            self.__button_do_action.config(text="Load",
                command=self.load_cookbook)
            pass
        elif mode == "export":
            # Exxport cookbook mode, place widgets to export cookbook and
            # configure correct button functions and text for labels
            self.title("MyCookBook - Export CookBook")

            # config functions for widgets
            self.__label_select_file_location.config(text="Export location:")
            self.__button_browse_location.config(
                command=lambda: self.browse_file("export"))
            self.__button_do_action.config(text="Export",
                command=lambda: self.export_cookbook(self.__export_choice))

            # place widgets with grid
            self.__label_select_export_type.grid(column=0, row=2, sticky="W")
            self.__radiobutton_export_external.grid(column=0, row=3,
                                                    sticky="W")
            self.__radiobutton_export_internal.grid(column=0, row=4,
                                                    sticky="W")

        # place cancel and action button to the bottom right corner with
        # grid, set row as 5 so that it is always bigger than other widgets
        # and hence will be placed in the correct position.
        self.__button_cancel.grid(column=0, row=5, sticky="SE")
        self.__button_do_action.grid(column=1, row=5, sticky="SE")

    def browse_file(self, action):
        """
        Open OS native filedialog. Param <action> determines what type of
        filedialog is opened

        1) action="load" Open dialog that asks user to select .cookbook file
        from the filedialog.
        2) action="save" Open dialog that asks user to enter filename for the
        file that will be saved (created).
        3) action = "export" Open dialog that asks user to select export
        directory.
        :param action: str, specifies what type of file dialog to open (load,
        new, export)

        if valid file path is chosen. The file path tkinter Entry widget will
        be updated with the new file path. If no valid path is chosen nothing
        will be done.
        :return: None
        """

        # check if action is load
        if action == "load":
            # open file dialog and ask for file location
            cookbook_path = filedialog.askopenfilename(
                title="Load cookbook:", filetypes=(("MyCookBook recipes",
                "*.cookbook"), ("all files", "*.*")))

        # check if action is save
        elif action == "save":
            # open save filedialog
            cookbook_path = filedialog.asksaveasfilename(
                defaultextension=".cookbook",
                title="Location for new cookbook:", filetypes=(
                ("MyCookBook recipes", "*.cookbook"), ("all files", "*.*")))

        # check if actions is export
        elif action == "export":
            # open directory dialog
            cookbook_path = filedialog.askdirectory(
                title="Select export directory:"
            )
        # set cookbook location to cookbook_path if path is not empty:
        if cookbook_path != "":
            # set selected file location to file location tkinter Entry textbox
            self.__entry_file_location.delete(0, END)
            self.__entry_file_location.insert(0, cookbook_path)
        else:
            # dialog canceled, do nothing
            pass

    def create_new_cookbook(self):
        """
        Function to process the file creation for the new cookbook.
        Gets file path from __cb_location StringVar. Checks if path is valid.
        If valid, will pass on cookbook path to function
        crate_new_cookbook(full_file_path) that is inside the MainWindow
        class. It will take care of the cookbook creation itself. If path is
        not valid, an error message will be displayed for the user.
        :return: None
        """
        # get the full file path
        full_file_path = self.__cb_location.get()

        # get the path without filename
        path_only = ospath.dirname(full_file_path)

        # check if the directory path exists
        if self.check_path(path_only):
            # proceed with creating cookbook
            # save current recipes before doing any editing to them
            self.root_window.save_recipes()

            # create new cookbook
            self.root_window.create_new_cookbook(full_file_path)

            # show success messagebox
            messagebox.showinfo(title="Cookbook created!",
                message="New cookbook created successfully!")

            # close window
            self.destroy()

    def load_cookbook(self):
        """
        Function to process the cookbook file loading.
        Gets file path from __cb_location StringVar. Checks if path is valid.
        If valid, will pass on cookbook path to function
        load_recipes() that is inside the MainWindow
        class. It will take care of the cookbook loading itself. If path is
        not valid, an error message will be displayed for the user. If
        cookbook can not be loaded, an error message will also be displayed.
        :return: None
        """
        # get the full file path
        full_file_path = self.__cb_location.get()

        # get checkbox selection for if the loaded cookbook should be set
        # as default (to be opened on startup)
        default_cb = self.__default_cookbook.get()

        # check if file path exists
        if self.check_path(full_file_path):

            # save current cookbook
            self.root_window.save_recipes()

            # proceed with loading file
            # pass on the value of checkbutton, determines if loaded recipe
            # will be set as default, to be loaded on startup
            if self.root_window.load_recipes(full_file_path, default_cb):
                # if loading of cookbook success, show success messagebox
                messagebox.showinfo(title="Recipes loaded!",
                    message="Recipes loaded successfully!")

                # close window
                self.destroy()
            else:
                # error loading files, show error messagebox
                messagebox.showinfo(title="Loading recipes failed!",
                    message="Error loading recipes! Maybe the file is"
                            " corrupted?")

    def export_cookbook(self, selection):
        """
        Function to process the cookbook exporting.
        Gets file path from __cb_location StringVar. Checks if path is valid.
        If valid, will pass on cookbook path to function
        load_recipes() that is inside the MainWindow
        class. It will take care of the cookbook exporting itself. <selection>
        param will also be passed, that tells the export function whether to
        export the cookbook as a .txt or .cookbook file. The selection is
        gotten by taking value from self.__export_choice, that changes
        depending on which radiobutton is selected.
        :param selection: IntVar(), the export selection (0 or 1)
        :return: None
        """
        # get the full file path
        export_dir = self.__cb_location.get()

        # check if the path directory exists
        if self.check_path(export_dir):
            # if directory exist, export cookbook
            # success message will be handeled by the export_cookbook_to_file
            # in MainWindow()
            self.root_window.export_cookbook_to_file(export_dir,
                self.__export_choice.get())

            # close window
            self.destroy()

    def check_path(self, path_to_check):
        """
        Cheks if path <path_to_check> is a valid path that exists on
        the computer. If the path exists, return True, else return false, and
        display an error message for the user.
        :param path_to_check: str, the path to check
        :return: bool, the result of the check.
        """

        # check if path <path_to_check> exists on computer
        if ospath.exists(path_to_check):
            # return True if path exists
            return True
        else:
            # else return False and display error message
            messagebox.showinfo(title="Invalid path!",
                message=f"File path does not exist or can not be accessed!")
            return False


class ViewRecipeWindow(Toplevel):

    def __init__(self, parent, root, recipe):
        """
        Initializes the ViewRecipeWindow as a new TopLevel tkinter
        window that inherits from parent MainWindow() This window is used
        to view selected <recipe> object recipe information (name, description,
        and ingredients).

        :param parent: tkinter.tkapp, the parent GUI.
        :param root: MainWindow object, allow access and communication
        to all MainWindow functions from ViewRecipeWindow
        :param recipe: object, the recipe object to view (get information
        from)
        """

        # Inherit from MainWindow with super()
        super().__init__()

        # set root_window as the "communications channel" for MainWindow
        # functions and methods
        self.root_window = root
        
        # set window title
        self.title("MyCookBook - View recipe")

        # create local version of font BUTTON_FONT
        self.__recipe_font = BUTTON_FONT

        # get what font type and size BUTTON_FONT is
        self.__button_font_type, self.__button_font_size \
            = BUTTON_FONT.split(" ")

        # create widgets
        self.__label_recipe_name = Label(self, text="Recipe name:",
            font=BIG_FONT)
        self.__label_selected_recipe_name = Label(self, text=recipe.get_name(),
            font=BIG_FONT)
        self.__label_recipe_desc = Label(self, text="Recipe description",
            font=BIG_FONT)
        # call it label even through it is a message widget because it
        # basically is a multiline label
        self.__label_selected_recipe_desc = Message(self,
            text=recipe.get_description(), font=self.__recipe_font)
        self.__label_recipe_ingredients = Label(self,
            text="Recipe ingredients:", font=BIG_FONT)
        self.__label_selected_recipe_ingredients = Message(self,
            text=recipe.get_ingredients(), font=self.__recipe_font)
        self.__label_font_size = Label(self,
            text=f"Font size: {self.__button_font_size}", font=BUTTON_FONT)
        self.__button_increment_font = Button(self,
            command=lambda: self.font_controller("+"), text="+",
            font=BUTTON_FONT)
        self.__button_decrement_font = Button(self,
            command=lambda: self.font_controller("-"), text="-",
            font=BUTTON_FONT)
        self.__button_close = Button(self, command=self.destroy, text="Close",
            font=BUTTON_FONT)

        # place widgets in correct position with pack()
        self.__label_recipe_name.pack(anchor="w", fill="both")
        self.__label_selected_recipe_name.pack(anchor="w", fill="both")
        self.__label_recipe_desc.pack(anchor="w", fill="both")
        self.__label_selected_recipe_desc.pack(anchor="w", fill="both")
        self.__label_recipe_ingredients.pack(anchor="w", fill="both")
        self.__label_selected_recipe_ingredients.pack(anchor="w", fill="both")
        self.__label_font_size.pack(side=LEFT, anchor="sw")
        self.__button_decrement_font.pack(side=LEFT, anchor="sw")
        self.__button_increment_font.pack(side=LEFT, anchor="sw")
        self.__button_close.pack(side=RIGHT, anchor="se")

    def font_controller(self, action):
        """
        Changes the recipe information labels font within a set range
        between 8 to 72. Makes font bigger if param action="+" and smaller if
        action="-". Updates all the labels with the new font.
        :param action:
        :return: None
        """
        # get the recipe FONT
        font_type = self.__button_font_type
        # get font size from recipe font (Eg. Arial 11) has font size 11
        font_size = int(self.__button_font_size)

        # check for action and make sure the font size is within a "valid"
        # range
        if action == "+" and font_size < 72:
            # increase font size
            font_size += 1
        elif action == "-" and font_size > 8:
            # decrease font size
            font_size -= 1
        else:
            # no conditions met return function and do no updates
            return

        # set the new font size
        # update widgets:
        for label in [self.__label_selected_recipe_name,
                      self.__label_selected_recipe_desc,
                      self.__label_selected_recipe_ingredients]:
            label.config(font=f"{font_type} {font_size}")

        # set updated font size and update font to label
        self.__label_font_size.config(text=f"Font size: {font_size}")
        self.__button_font_size = font_size


class EditRecipeWindow(Toplevel):

    def __init__(self, parent, root, mode="add", recipe=None):
        """
        Initializes the EditRecipeWindow as a new TopLevel tkinter
        window that inherits from parent MainWindow() This window has two
        uses depending on param <mode>.

        1) mode="add" (default) Add new recipe to MainWindow recipes list.
        2) mode"edit" Edit recipe object supplied by <recipe> param

        The GUI is adjusted accordingly to the <mode> and the widgets are
        updated with correct values.

        :param parent: tkinter.tkapp, the parent GUI.
        :param root: MainWindow object, allow access and communication
        to all MainWindow functions from ViewRecipeWindow
        :param mode: str, the mode to operate in (add or edit recipe)
        :param recipe: object, recipe object to edit (if mode="edit")
        """
        # Inherit from MainWindow() with super()
        super().__init__()

        # set root_window as the "communications channel" for MainWindow
        # functions and methods
        self.root_window = root

        # set window size
        self.geometry("800x600")
        # set minimum window size
        self.minsize(width=400, height=500)

        # create widgets
        self.__label_recipe_name = Label(self, text="Recipe name:",
                                         font=BIG_FONT)
        self.__entry_recipe_name = Entry(self, font=BIG_FONT)
        self.__label_recipe_desc = Label(self, text="Recipe description",
                                         font=BIG_FONT)
        self.__text_recipe_desc = Text(self, width=50, height=15,
                                       font=BUTTON_FONT)
        self.__label_recipe_ingredients = Label(self,
                                                text="Recipe ingredients:",
                                                font=BIG_FONT)
        self.__label_of_ingredient = Label(self, text="of", font=BIG_FONT,
                                           width=5)
        self.__text_ingredients = Text(self, width=50, height=10,
                                       font=BUTTON_FONT)
        self.__label_info = Label(self,
                                  text="Enter each ingredient on new line.",
                                  font=BUTTON_FONT)
        self.__button_create_recipe = Button(self, text="Add",
                                             command=self.add_recipe,
                                             font=BUTTON_FONT)
        self.__button_cancel = Button(self, text="Cancel",
                                      command=self.destroy, font=BUTTON_FONT)

        # place widgets in correct position with pack()
        self.__label_recipe_name.pack(anchor="w")
        self.__entry_recipe_name.pack(anchor="w", fill="x")
        self.__label_recipe_desc.pack(anchor="w")
        self.__text_recipe_desc.pack(anchor="w", fill="both", expand=True)
        self.__label_recipe_ingredients.pack(anchor="w")
        self.__text_ingredients.pack(anchor="w", fill="both", expand=True)
        self.__label_info.pack(anchor="w")
        self.__button_create_recipe.pack(side=RIGHT, anchor="se")
        self.__button_cancel.pack(side=RIGHT, anchor="se")

        # default mode is "add", if mode is edit:
        if mode == "edit":
            # EDIT MODE, fill recipe info to Entry textboxes
            self.title("MyCookBook - Edit recipe")

            # prefill recipe info
            self.__recipe = recipe
            # get recipe name and insert it to textbox
            self.__entry_recipe_name.insert(0, self.__recipe.get_name())
            # get recipe description and insert it to multiline textbox
            self.__text_recipe_desc.insert(1.0,
                                           self.__recipe.get_description())
            # get recipe ingredients and insert it to multiline textbox
            self.__text_ingredients.insert(1.0,
                                           self.__recipe.get_ingredients())
            # change the create recipe button text to edit and change
            # the command to commit edit.
            self.__button_create_recipe.config(text="Edit",
                                               command=self.edit_recipe)
        else:
            # DEFAULT: "add" mode: Set title as Add recipe
            self.title("MyCookBook - Add recipe")

    def process_entry_values(self):
        """
        This function processes the tkinter Entry widget values. Checks that
        that the recipe name and recipe ingredients are not empty. If invalid
        values are found, False is returned and an error message is displayed
        to the user. For valid input the recipe name, description and
        ingredients are returned as string.
        :return: bool/str, None/str, None/str, if false the values on the left
        side of the / char are returned, if true the values on right side of
        the / char are returned.
        """

        # get the recipe name, description and ingredients from textboxes
        recipe_name = self.__entry_recipe_name.get()
        recipe_desc = self.__text_recipe_desc.get(1.0, END)
        recipe_ingredients = self.__text_ingredients.get(1.0, END)

        # check that the values are valid
        # initialize a string that error messages are appended to
        errormessage = ""

        # check if the recipe name is atleast one character long
        if len(recipe_name) < 1:
            # if not, add to errormessage
            errormessage += "The recipe name must be over 0 characters long."

        # check if the recipe ingredients is atleast 2 charachters long
        # (completely artificial number, but there are surely no ingredients
        # that are under two characters...
        if len(recipe_ingredients) < 2:
            # if not, add to errormessage
            errormessage += "\nThe recipe needs to have at least one" \
                            " ingredient"

        # check if error were detected, if the erromessage str is not empty
        # errors have been detected
        if errormessage != "":
            # if errors detected, show errors and return False
            messagebox.showinfo(title="Error adding recipe!",
                                message=errormessage)
            return False, None, None

        # checks success, return recipe name, description and ingredients:
        return recipe_name, recipe_desc, recipe_ingredients

    def edit_recipe(self):
        """
        Process the recipe edit. Check that the edited values are valid with
        process_entry_values() function. If the values are valid, proceed
        to commit recipe edit. Edited recipe object is created, and sent
        as a param to MainWindow function save_edit() to be added to the
        MainWindow recipes list in the correct index position.
        :return: None
        """

        # get recipe name, description and ingredients
        recipe_name, recipe_desc, recipe_ingredients \
            = self.process_entry_values()

        # if recipe_name is False, means that the process values function
        # failed to get the correct recipe information
        if recipe_name is False:
            # error occurred, return
            return

        # no errors, proceed to edit
        # get edited recipe index
        recipe_index = self.__recipe.get_index()

        # Create new recipe object that will replace the old pre-edited
        # recipe object with the same index
        recipe_to_add = Recipe(recipe_name, recipe_desc, recipe_ingredients,
                               recipe_index)

        # sen recipe to MainWindow save_edit function to be committed
        # to the correct index in the recipes list
        self.root_window.save_edit(recipe_to_add)

        # close window
        self.destroy()

    def add_recipe(self):
        """
        Process the recipe creation. Check that the edited values are valid
        with process_entry_values() function. If the values are valid, proceed
        to commit recipe creation. New recipe object is created, and sent
        as a param to MainWindow function add_recipe() to be appended to the
        MainWindow recipes list.
        :return: None
        """

        # get recipe name, description and ingredients
        recipe_name, recipe_desc, recipe_ingredients \
            = self.process_entry_values()

        # if recipe_name is False, means that the process values function
        # failed to get the correct recipe information
        if recipe_name is False:

            # error occurred, return
            return

        # get biggest index of all recipes in the recipes list, assign new
        # recipe bigger index
        recipe_index = self.root_window.get_biggest_index() + 1

        # Create new recipe object
        recipe_to_add = Recipe(recipe_name, recipe_desc, recipe_ingredients,
                               recipe_index)

        # send created recipe object to MainWindow add_recipe function to be
        # added to the recipes list
        self.root_window.add_recipe(recipe_to_add)

        # close window
        self.destroy()


def main():
    # start the APP
    MainWindow()


if __name__ == "__main__":
    main()
