import tkinter as tk
from tkinter import messagebox
import random
import requests ### NEW ### - Library to make web requests

#=======================================================================
### NEW ### - CONFIGURATION SETTING
# Change this value to "API" to use the online dictionary API,
# or "LOCAL" to use the words.txt file.
WORD_SOURCE = "API" 
#=======================================================================


### NEW ### - Function to get a random word from an online API
def get_word_from_api():
    """Fetches a random word from a free dictionary API."""
    try:
        # This API gives a single random word in a JSON list, e.g., ["word"]
        response = requests.get("https://random-word-api.herokuapp.com/word")
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # The response is a JSON list, so we get the first element
            word = response.json()[0].upper()
            print(f"Successfully fetched word from API") # For debugging
            return word
        else:
            return None # Indicate failure
    except requests.exceptions.RequestException as e:
        # Handle network errors (e.g., no internet connection)
        print(f"API request failed: {e}") # For debugging
        return None


### MODIFIED ### - Function to get a word from the local words.txt file
def get_word_from_local_file():
    """Chooses a random word from the words.txt file."""
    try:
        with open("words.txt", "r") as file:
            words = [word.strip().upper() for word in file.readlines()]
            if not words:
                messagebox.showerror("Error", "words.txt is empty! Please add words to it.")
                return "EMPTY"
            return random.choice(words)
    except FileNotFoundError:
        messagebox.showerror("Error", "words.txt not found!\nPlease create it in the same directory.")
        return None

### MODIFIED ### - The main function to choose a word based on the configuration
def choose_word():
    """
    Chooses a random word based on the WORD_SOURCE setting.
    It will try the API first if set, but fall back to the local file on failure.
    """
    word = None
    if WORD_SOURCE == "API":
        word = get_word_from_api()
        if word:
            return word
        else:
            # Fallback message
            messagebox.showwarning("API Failed", "Could not fetch a word from the internet. Falling back to local words.txt file.")
            # Fallback to local file
            return get_word_from_local_file()
            
    # If source is "LOCAL" or API failed, use the local file.
    return get_word_from_local_file()


# --- ASCII art for the hangman (unchanged) ---
HANGMAN_PICS = [
    '''
       +---+
           |
           |
           |
          ===
    ''',
    '''
       +---+
       O   |
           |
           |
          ===
    ''',
    '''
       +---+
       O   |
       |   |
           |
          ===
    ''',
    '''
       +---+
       O   |
      /|   |
           |
          ===
    ''',
    '''
       +---+
       O   |
      /|\\  |
           |
          ===
    ''',
    '''
       +---+
       O   |
      /|\\  |
      /    |
          ===
    ''',
    '''
       +---+
       O   |
      /|\\  |
      / \\  |
          ===
    '''
]
# --- Main Application Class (unchanged) ---
class HangmanGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Hangman Game")
        self.master.geometry("400x500")

        self.word = ""
        self.word_completion = []
        self.guessed_letters = []
        self.tries = 6

        self.hangman_label = tk.Label(self.master, text="", font=("Courier", 12), justify=tk.LEFT)
        self.hangman_label.pack(pady=10)

        self.word_label = tk.Label(self.master, text="", font=("Helvetica", 24, "bold"))
        self.word_label.pack(pady=10)

        self.guessed_label = tk.Label(self.master, text="", font=("Helvetica", 12))
        self.guessed_label.pack(pady=5)

        input_frame = tk.Frame(self.master)
        input_frame.pack(pady=20)

        self.guess_entry = tk.Entry(input_frame, width=5, font=("Helvetica", 18))
        self.guess_entry.pack(side=tk.LEFT, padx=5)
        self.master.bind('<Return>', lambda event: self.make_guess())

        self.guess_button = tk.Button(input_frame, text="Guess", command=self.make_guess, font=("Helvetica", 12))
        self.guess_button.pack(side=tk.LEFT)

        self.new_game_button = tk.Button(self.master, text="New Game", command=self.setup_new_game, font=("Helvetica", 14))
        self.new_game_button.pack(pady=10)

        self.setup_new_game()

    # ALL THE METHODS BELOW THIS (setup_new_game, update_display, etc.) ARE THE SAME
    # No changes are needed in the GUI logic itself.
    def setup_new_game(self):
        """Resets the game state for a new round."""
        self.word = choose_word() # This now uses our new flexible function
        if self.word is None or self.word == "EMPTY":
            if self.word is None:
                self.word_label.config(text="File not found!")
            else:
                self.word_label.config(text="File is empty!")
            self.guess_entry.config(state='disabled')
            self.guess_button.config(state='disabled')
            return

        self.word_completion = ['_'] * len(self.word)
        self.guessed_letters = []
        self.tries = 6
        self.guess_entry.config(state='normal')
        self.guess_button.config(state='normal')
        self.guess_entry.delete(0, tk.END)
        self.update_display()

    def update_display(self):
        """Updates all the labels on the screen with the current game state."""
        self.hangman_label.config(text=HANGMAN_PICS[6 - self.tries])
        self.word_label.config(text=" ".join(self.word_completion))
        self.guessed_label.config(text=f"Guessed: {', '.join(sorted(self.guessed_letters))}")

    def make_guess(self):
        """Processes the user's guess."""
        guess = self.guess_entry.get().upper()
        self.guess_entry.delete(0, tk.END)

        if not guess.isalpha() or len(guess) != 1:
            messagebox.showwarning("Invalid Input", "Please enter a single letter.")
            return

        if guess in self.guessed_letters:
            messagebox.showinfo("Already Guessed", f"You have already guessed the letter '{guess}'.")
            return

        self.guessed_letters.append(guess)

        if guess in self.word:
            for i, letter in enumerate(self.word):
                if letter == guess:
                    self.word_completion[i] = guess
        else:
            self.tries -= 1

        self.update_display()
        self.check_game_over()

    def check_game_over(self):
        """Checks for win or loss conditions and shows a message."""
        if '_' not in self.word_completion:
            messagebox.showinfo("You Win!", f"Congratulations! You guessed the word: {self.word}")
            self.end_game()
        elif self.tries == 0:
            self.hangman_label.config(text=HANGMAN_PICS[6])
            messagebox.showinfo("Game Over", f"You lost! The word was: {self.word}")
            self.end_game()

def end_game(self):
        """Disables the guessing controls at the end of the game."""
        self.guess_entry.config(state='disabled')
        self.guess_button.config(state='disabled')
        
# --- Main execution block (unchanged) ---
if __name__ == "__main__":
    root = tk.Tk()
    # ... etc ...


# --- Main execution block (unchanged) ---
if __name__ == "__main__":
    root = tk.Tk()
    app = HangmanGUI(root)

    root.mainloop()
