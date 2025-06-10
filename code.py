import cv2
import dlib
import numpy as np
import tkinter as tk
from collections import Counter
import threading
import time

# Load dlib's face detector and landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(r"D:\studies\project\code\shape_predictor_68_face_landmarks.dat")

# Word corpus
word_corpus = ["ALARM", "ALL", "AND", "ANGRY", "ANNA UNIVERSITY", "ARE", "AT", "BABY", "BAD", "BAG", "BANK", "BATHROOM", "BATHE", "BE", "BED", "BEDROOM", "BEGIN", "BEST", "BIG", "BOOK", "BOTTLE", "BRING", "BRUSH", "BROTHER", "BUY", "CALL", "CAN", "CAN YOU HEAR ME?", "CARRY", "CHAIR", "CHARGE", "CHECK", "CHILD", "CLEAN", "CLOCK", "CLOTHES", "CLOSE", "COFFEE", "COLLEGE", "COME", "COME HERE", "COIMBATORE", "COOK", "COOL", "COUCH", "COULD", "CROSS", "DAD", "DEPARTMENT", "DESK", "DID", "DINING", "DIRTY", "DOCTOR", "DONE", "DOOR", "DRESS", "DRINK", "DRIVE", "EACH", "EARLY", "EAT", "EGG", "END", "ENTER", "EVEN", "EVERY", "FAMILY", "FAST", "FEED", "FEEL", "FINE", "FISH", "FIX", "FOOD", "FOR", "FREE", "FRIEND", "FROM", "FRUIT", "GET", "GONE", "GOOD", "GOOD AFTERNOON", "GOOD MORNING", "GOOD NIGHT", "GO", "GO THERE", "GYM", "HALL", "HAPPY", "HARD", "HAVE", "HE", "HEAR", "HEAT", "HELLO", "HELP", "HER", "HIS", "HOME", "HOSPITAL", "HOT", "HOUR", "HOUSE", "HOW", "HOW ARE YOU?", "HUNGRY", "I", "I AM FEELING COLD", "I AM FINE", "I AM IN PAIN", "I AM TIRED", "I NEED FOOD", "I NEED MY PHONE", "I NEED TO GO", "I NEED WATER", "I WANT TO EAT", "I WANT TO SLEEP", "IN A", "IS THE", "IT", "IT IS TOO HOT", "JUMP", "JUST", "KEEP", "KEYS", "KITCHEN", "KNOW", "LAPTOP", "LATE", "LEAVE", "LESS", "LIKE", "LISTEN", "LITTLE", "LOOK", "MAKE", "MALL", "MARKET", "MADE", "MEAT", "MEET", "MINUTE", "MILK", "MOM", "MORE", "MORNING", "MOVE", "NEIGHBOR", "NIGHT", "NO", "NONE", "NOT", "NOW", "OFFICE", "OKAY", "ONE", "OPEN", "OUTSIDE", "PART", "PARK", "PATIENT", "PAY", "PEOPLE", "PHONE", "PLAN", "PLAY", "PLEASE", "PLEASE CALL THE DOCTOR", "PLEASE HELP ME", "PLEASE TURN ON THE LIGHT", "QUICK", "QUIT", "RICE", "READ", "RECEIVE", "RESTAURANT", "REST", "RIGHT", "ROAD", "ROOM", "RUN", "SAID", "SAD", "SCHOOL", "SECOND", "SEE", "SEND", "SHE", "SHOP", "SHOES", "SHOWER", "SICK", "SIT", "SISTER", "SLEEP", "SLOW", "SMALL", "SOME", "SORRY", "SOFT", "START", "STAND", "STOP", "STREET", "STUDENT", "SCHOOL", "TABLE", "TAKE", "TALK", "TEACHER", "TEA", "THANK YOU", "THANKS", "THAT", "THEY", "THERE", "THINK", "THIS", "THIRSTY", "TIRED", "TODAY", "TOMORROW", "TOUCH", "TURN LEFT", "TURN RIGHT", "TV", "UNDER", "USE", "VERY", "VOICE", "WAIT", "WALK", "WANT", "WARM", "WASH", "WATCH", "WATER", "WE", "WEAR", "WHAT", "WHAT TIME IS IT?", "WHEN", "WHERE", "WHERE ARE YOU?", "WHICH", "WHO", "WHY", "WILL", "WINDOW", "WORK", "WRITE", "XEROX", "YES", "YOU", "YOUR", "ZERO", "ZOO"]
word_counts = Counter(word_corpus)

# Keyboard layouts
letter_layout = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
                 "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                 "U", "V", "W", "X", "Y", "Z", "Space", "Suggestion", "Backspace", "Clear", "123", "#@&", "Fast Fillers","Emoji", "Exit"]

number_layout = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
                 "Backspace", "Clear", "ABC", "#@&","Emoji", "Exit"]

symbol_layout = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")",
                 "Backspace", "Clear", "ABC", "123","Emoji","Exit"]

fast_filler_words = ["THE", "AN", "IN", "ON", "AT", "TO", "BY", "WITH", "FOR", "OF", "FROM", "AND", "BUT", "OR", "SO", "IT", "HE", "SHE", "THEY"
                     ,"WE","US","BECAUSE","WAS","WERE","DOES","DON'T","YOUR","ARE","HAVE","HAS"]
emoji_layout = ["😀", "😂", "😍", "😢", "😎", "😡", "👍", "🙏", "👏", "💖",
                "Backspace", "Clear", "ABC", "123", "Exit"]


control_keys = ["ABC", "123", "#@&", "Space", "Backspace", "Exit"]
filler_layout = fast_filler_words + control_keys

current_layout = letter_layout
selected_key = 0
buttons = []

# Suggestion and Fast Fillers variables
in_suggestion_mode = False
suggestions = []
selected_suggestion_index = 0

# GUI
root = tk.Tk()
root.title("AI Eye-Controlled Keyboard")

# Time & Blink Detection
time_to_wait = 0.5  # Slower delay for responsiveness, as in your previous code
last_key_time = time.time()
blink_threshold = 0.22

# Widgets
text_area = None
suggestion_label = None
letter_guide = None

def predict_word():
    input_text = text_area.get("1.0", tk.END).strip().upper().split(" ")
    last_word = input_text[-1] if input_text else ""
    if last_word:
        global suggestions
        suggestions = [word for word in word_corpus if word.startswith(last_word)]
        suggestion_label.config(text="Suggestions: " + ", ".join(suggestions[:3]).upper())
    else:
        suggestion_label.config(text="Suggestions: ")

def apply_suggestion():
    global in_suggestion_mode, suggestions, selected_suggestion_index
    input_text = text_area.get("1.0", tk.END).strip().upper().split(" ")
    last_word = input_text[-1] if input_text else ""
    suggestions = [word for word in word_corpus if word.startswith(last_word)]
    if suggestions:
        in_suggestion_mode = True
        selected_suggestion_index = 0
        update_suggestion_navigation("")

def select_suggestion():
    global in_suggestion_mode
    words = text_area.get("1.0", tk.END).strip().split(" ")
    if words and suggestions:
        words[-1] = suggestions[selected_suggestion_index].upper()
        text_area.delete("1.0", tk.END)
        text_area.insert(tk.END, " ".join(words) + " ")
        suggestion_label.config(text=f"Selected: {suggestions[selected_suggestion_index].upper()}")
    in_suggestion_mode = False

def update_suggestion_navigation(direction):
    global selected_suggestion_index
    if not suggestions:
        return
    if direction == "left":
        selected_suggestion_index = (selected_suggestion_index - 1) % len(suggestions)
    elif direction == "right":
        selected_suggestion_index = (selected_suggestion_index + 1) % len(suggestions)
    suggestion_label.config(text="Choose: " + ", ".join(
        [f"[{s.upper()}]" if i == selected_suggestion_index else s.upper() for i, s in enumerate(suggestions[:10])]))

def update_keyboard():
    if in_suggestion_mode:
        return
    letter_guide.config(text=f"Selected: {current_layout[selected_key]}")
    for i, btn in enumerate(buttons):
        if i < len(current_layout):
            btn.config(text=current_layout[i], bg="yellow" if i == selected_key else "lightgray")
        else:
            btn.config(text="", bg="SystemButtonFace")

def backspace():
    text = text_area.get("1.0", tk.END).strip()
    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, text[:-1])
    predict_word()

def clear_text():
    text_area.delete("1.0", tk.END)
    suggestion_label.config(text="Suggestions: ")

def close_keyboard():
    root.quit()

def switch_layout(new_layout):
    global current_layout, selected_key
    current_layout = new_layout
    selected_key = 0
    update_keyboard()

def handle_fast_fillers():
    switch_layout(filler_layout)

def type_letter():
    global last_key_time, in_suggestion_mode
    current_time = time.time()
    if current_time - last_key_time < time_to_wait:
        return
    last_key_time = current_time

    if in_suggestion_mode:
        select_suggestion()
        return

    key = current_layout[selected_key]
    if key == "Backspace":
        root.after(0, backspace)
    elif key == "Clear":
        root.after(0, clear_text)
    elif key == "Exit":
        root.after(0, close_keyboard)
    elif key == "123":
        switch_layout(number_layout)
    elif key == "#@&":
        switch_layout(symbol_layout)
    elif key == "ABC":
        switch_layout(letter_layout)
    elif key == "Suggestion":
        root.after(0, apply_suggestion)
    elif key == "Space":
        root.after(0, lambda: text_area.insert(tk.END, " "))
        root.after(0, predict_word)
    elif key == "Fast Fillers":
        root.after(0, handle_fast_fillers)
    elif key in fast_filler_words:
        root.after(0, lambda: text_area.insert(tk.END, key + " "))
        root.after(0, predict_word)
    elif key == "Emoji":
        switch_layout(emoji_layout)
    elif key in emoji_layout:
        root.after(0, lambda: text_area.insert(tk.END, key + " "))

    else:
        root.after(0, lambda: text_area.insert(tk.END, key))
        root.after(0, predict_word)
    print(f"Typed: {key}")

def setup_keyboard():
    global text_area, suggestion_label, letter_guide
    text_area = tk.Text(root, height=3, width=40, font=("Arial", 16))
    text_area.grid(row=0, column=0, columnspan=5)

    letter_guide = tk.Label(root, text="Selected: A", font=("Arial", 14), fg="blue")
    letter_guide.grid(row=1, column=0, columnspan=5)

    suggestion_label = tk.Label(root, text="Suggestions: ", font=("Arial", 14))
    suggestion_label.grid(row=2, column=0, columnspan=5)

    instructions = tk.Label(root, text="\U0001F537 Blink to Type | Look Left/Right to Navigate",
                            font=("Arial", 12), fg="green")
    instructions.grid(row=3, column=0, columnspan=5)

    for i in range(40):
        btn = tk.Button(root, text="", width=8, height=3, font=("Arial", 16))
        btn.grid(row=4 + i // 6, column=i % 6)
        buttons.append(btn)

    update_keyboard()

def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C)

def run_webcam():
    global selected_key
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot access camera")
        return

    last_dir_time = time.time()
    direction_change_cooldown = 0.8  # Increased cooldown time to slow down navigation

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        if len(faces) == 0:
            continue

        for face in faces:
            landmarks = predictor(gray, face)
            left_eye = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(36, 42)])
            right_eye = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(42, 48)])
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)
            ear = (left_ear + right_ear) / 2.0

            if ear < blink_threshold:
                type_letter()

            dx = left_eye[3][0] - left_eye[0][0]
            direction = None
            if dx > 15:
                direction = "right"
            elif dx < -15:
                direction = "left"

            if direction and (time.time() - last_dir_time > direction_change_cooldown):
                if in_suggestion_mode:
                    update_suggestion_navigation(direction)
                else:
                    if direction == "left":
                        selected_key = (selected_key - 1) % len(current_layout)
                    elif direction == "right":
                        selected_key = (selected_key + 1) % len(current_layout)
                    update_keyboard()
                last_dir_time = time.time()

        cv2.imshow("Eye Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Launch GUI and Webcam
setup_keyboard()
webcam_thread = threading.Thread(target=run_webcam, daemon=True)
webcam_thread.start()
root.mainloop()