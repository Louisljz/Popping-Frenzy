# Imports
import pygame
import cv2
from cvzone.HandTrackingModule import HandDetector
import time
import random
import os
import sys
import pandas as pd

# Initialize and Create Window
pygame.init()

width, height = 1280, 720
window = pygame.display.set_mode((width,height))
pygame.display.set_caption('Lampion Blast')

# Initialize clock for FPS
fps = 30
clock = pygame.time.Clock()

# Set Folder Path according to exe or py file that is being run
if getattr(sys, 'frozen', False):
    folder_path = os.path.dirname(sys.executable)
else:
    folder_path = os.path.dirname(__file__)

# Load Resources
resources_path = os.path.join(folder_path, 'Resources/')
database = os.path.join(resources_path, 'database.csv')

bgmusic_path = os.path.join(resources_path, 'BG Music/')
sfx_path = os.path.join(resources_path, 'SFX/')
fonts_path = os.path.join(resources_path, 'Fonts/')
images_path = os.path.join(resources_path, 'Images/')

# Load BG Music
homeMusic = pygame.mixer.Sound(os.path.join(bgmusic_path, 'homeMusic.mp3'))
homeMusic.set_volume(0.5)
gameMusic = pygame.mixer.Sound(os.path.join(bgmusic_path, 'gameMusic.mp3'))
gameMusic.set_volume(0.5)
endMusic = pygame.mixer.Sound(os.path.join(bgmusic_path, 'endMusic.mp3'))
endMusic.set_volume(0.5)

# Load Sound Effects
pop_sfx = pygame.mixer.Sound(os.path.join(sfx_path, 'pop.mp3'))
pop_sfx.set_volume(1)
transition = pygame.mixer.Sound(os.path.join(sfx_path, 'transition.mp3'))
transition.set_volume(1)
boom = pygame.mixer.Sound(os.path.join(sfx_path, 'boom.mp3'))
boom.set_volume(1)

# Load Fonts
font1_100 = pygame.font.Font(os.path.join(fonts_path, 'aAsianNinja.ttf'), 100)
font1_70 = pygame.font.Font(os.path.join(fonts_path, 'aAsianNinja.ttf'), 70)
font2_50 = pygame.font.Font(os.path.join(fonts_path, 'go3v2.ttf'), 50)
font2_100 = pygame.font.Font(os.path.join(fonts_path, 'go3v2.ttf'), 100)
leaderboard_font = pygame.font.Font(os.path.join(fonts_path, 'AgencyFB-Bold.ttf'), 50)

# Load Images
home_path = os.path.join(images_path, 'Home/')
game_path = os.path.join(images_path, 'Game/')
end_path = os.path.join(images_path, 'End/')

# Set App Icon
icon = pygame.image.load(os.path.join(images_path, 'app-icon.png')).convert_alpha()
pygame.display.set_icon(icon)

# Set Cursor
cursor = pygame.image.load(os.path.join(images_path, 'cursor.png')).convert_alpha()

# Home Screen Images
homeBG = pygame.image.load(os.path.join(home_path, 'homeBG.jpg')).convert()

playBtn = pygame.image.load(os.path.join(home_path, 'playBtn.png')).convert_alpha()
playBtnRect = playBtn.get_rect()
playBtnRect.x = 150
playBtnRect.y = height/2 - 200

# Game Screen Images
gameBG = pygame.image.load(os.path.join(game_path, 'gameBG.jpg')).convert()
dart = pygame.image.load(os.path.join(game_path, 'dart.png')).convert_alpha()
pop_sprite = pygame.image.load(os.path.join(game_path, 'pop.png')).convert_alpha()
bonus_pop = pygame.image.load(os.path.join(game_path, 'bonus_pop.png')).convert_alpha()

# Lampions
lampion1 = pygame.image.load(os.path.join(game_path, 'lampion1.png')).convert_alpha()
lampion_rect1 = lampion1.get_rect()

lampion2 = pygame.image.load(os.path.join(game_path, 'lampion2.png')).convert_alpha()
lampion_rect2 = lampion2.get_rect()

lampion3 = pygame.image.load(os.path.join(game_path, 'lampion3.png')).convert_alpha()
lampion_rect3 = lampion3.get_rect()

lampion4 = pygame.image.load(os.path.join(game_path, 'lampion4.png')).convert_alpha()
lampion_rect4 = lampion4.get_rect()

special_lampion = pygame.image.load(os.path.join(game_path, 'special lampion.png')).convert_alpha()
special_lampion_rect = special_lampion.get_rect()

lampion_rects = {'lampion_rect1': lampion_rect1,
                'lampion_rect2': lampion_rect2,
                'lampion_rect3': lampion_rect3,
                'lampion_rect4': lampion_rect4,
                'special_lampion_rect': special_lampion_rect}

lampion_images = {'lampion1': lampion1,
                'lampion2': lampion2,
                'lampion3': lampion3,
                'lampion4': lampion4,
                'special_lampion': special_lampion}

# Curtains
curtainsLeft = pygame.image.load(os.path.join(game_path, 'CurtainsLeft.png')).convert_alpha()
curtainsLeftRect = curtainsLeft.get_rect()
curtainsLeftRect.x = 0
curtainsLeftRect.y = 0

curtainsRight = pygame.image.load(os.path.join(game_path, 'CurtainsRight.png')).convert_alpha()
curtainsRightRect = curtainsRight.get_rect()
curtainsRightRect.x = width - 515
curtainsRightRect.y = 0

# End Screen Images
endBG = pygame.image.load(os.path.join(end_path, 'EndBG.png')).convert()
textFrame = pygame.image.load(os.path.join(end_path, 'textFrame.png')).convert_alpha()

backbtn = pygame.image.load(os.path.join(end_path, 'back.png')).convert_alpha()
backbtn_rect = backbtn.get_rect()
backbtn_rect.x = 200
backbtn_rect.y = 70

quitbtn = pygame.image.load(os.path.join(end_path, 'quit.png')).convert_alpha()
quitbtn_rect = quitbtn.get_rect()
quitbtn_rect.x = width-350
quitbtn_rect.y = 70


# Webcam
cap = cv2.VideoCapture(1)
cap.set(3, width)
cap.set(4, height)

# Hand Tracking
detector = HandDetector(maxHands=1)

# Reset Lampions when out of frame or popped.
x_points = [100, 300, 500, 700, 900, 1100] # List of possible respawn points
def reset_lampions(keyRect, y=height):
    rect = lampion_rects[keyRect]

    keys = list(lampion_rects.keys())
    values = list(lampion_rects.values())
    index = keys.index(keyRect)
    values.pop(index)

    rect.y = y
    while True:
        rect.x = random.choice(x_points)
        if rect.collidelist(values) == -1: 
            # Make sure the lampions don't overlap each other
            break

# Reset Initial Position of Lampions
def position_lampions():
    lampion_rect1.x = 200
    lampion_rect1.y = 700

    lampion_rect2.x = 400
    lampion_rect2.y = 700

    lampion_rect3.x = 630
    lampion_rect3.y = 700

    lampion_rect4.x = 880
    lampion_rect4.y = 700

    special_lampion_rect.x = width
    special_lampion_rect.y = 700

# Keyboard Buttons for Name Scene
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L"], 
        ["Z", "X", "C", "V", "B", "N", "M"]] 

# Generate Button Instances for every key
class Button():
    def __init__(self, pos, text, size=(85, 85)):
        self.pos = pos
        self.size = size
        self.text = text

    def getRect(self):
        return pygame.rect.Rect(self.pos, self.size)

buttonList = []
for i in range(len(keys)): # Rows
    for j, key in enumerate(keys[i]): # Columns
        buttonList.append(Button((100 * j + 50, 100 * i + 50), key))

# Backspace Key (takes 3 cells)
x, y, w, h = 750, 250, 290, 85
buttonList.append(Button((x,y), 'Backspace', (w,h)))

# Enter Key (takes 3 cells)
x, y, w, h = 850, 350, 290, 85
buttonList.append(Button((x,y), 'Enter', (w,h)))

# Draw all keyboard buttons
def drawKeys():
    # Special for Unused Key
    x, y, w, h = 950, 150, 85, 85
    pygame.draw.rect(window, (255, 0, 255), (x, y, w, h))
    for button in buttonList:
        x, y = button.pos
        w, h = button.size

        pygame.draw.rect(window, (255, 0, 255), (x, y, w, h))
        letter = font2_50.render(button.text, True, (255, 255, 255))
        window.blit(letter, (x + 20, y + 30))

# Read database, get top 5 highest score.
def get_leaderboard():
    db = pd.read_csv(database)
    db = db.sort_values(by='score', ascending=False)
    if len(db) > 5:
        names = db['name'].iloc[:5].to_numpy()
        scores = db['score'].iloc[:5].to_numpy()
    else:
        names = db['name'].to_numpy()
        scores = db['score'].to_numpy()

    return names, scores

# Write score data to CSV file
def write_score(name, score):
    db = pd.read_csv(database)
    row = pd.Series({'name': name, 'score': score})
    new_db = pd.concat([db, pd.DataFrame([row], columns=row.index)])
    new_db.to_csv(database, index=False)

# Detect Hand from Webcam
def hand_detector(scale = 75):
    # scale = scale/100
    _, img = cap.read()
    img = cv2.flip(img, 1)
    # img = img[int(height-height*scale) : int(height*scale), 
    #         int(width-width*scale) : int(width*scale)] 
    # img = cv2.resize(img, (1280, 720))
    hands = detector.findHands(img, flipType=False, draw=False)
    return hands

# Scene Manager
class SceneManager:
    def __init__(self, duration = 45, initial_speed = 5, increase_speed=0.35):
        self.duration = duration
        self.initial_speed = initial_speed
        self.increase_speed = increase_speed
        # variable for changing scenes
        self.state = 'home' 
        self.names, self.scores = get_leaderboard()
        self.counter = 0 # Wait for 3 seconds to click

    def displayHomeScreen(self):
        # Display UI
        window.blit(homeBG, (0,0))
        window.blit(playBtn, playBtnRect)

        title = font1_100.render('Lampion Blast', True, 
                            (255, 255, 255))
        window.blit(title, (350, 20))

        leaderboard_title = leaderboard_font.render('LEADERBOARD', True, (255,255,0))
        window.blit(leaderboard_title, (815, 225))

        # Display the Database
        for i in range(len(self.names)):
            text = leaderboard_font.render(f'{i+1}. {self.names[i]}: {self.scores[i]}',
                                    True, (255,255,0))
            window.blit(text, (825, i * 55 + 300))
        
        hands = hand_detector()
        
        if hands:
            hand = hands[0]
            lmList = hand['lmList']
            fingers = detector.fingersUp(hand) 

            # If teach finger is up..
            if fingers[1] == 1:
                # Get X, Y coordinate of the end point of teach finger
                teachX, teachY = lmList[8][0:2] 
                # Display cursor
                window.blit(cursor, (teachX-25, teachY-30))
                # and if the teach finger collides with the button..
                if playBtnRect.collidepoint(teachX, teachY):
                    self.counter += 1
                    if self.counter == 40: # Almost 2 seconds
                        self.counter = 0
                        self.nameText = ''
                        self.state = 'name'

                else:
                    self.counter = 0
    
    def displayNameScreen(self):
        # Display BG
        window.blit(homeBG, (0,0))
        hands = hand_detector()

        # Set Char limit for Name
        if len(self.nameText) > 8:
            max = True
            warning = font1_70.render('Maximum Word Number Reached: 8',
                                        True, (255,0,0), (255,255,255))
            window.blit(warning, (100, 500))
        else:
            max = False
        
        # Make Sure Name is not Blank
        if len(self.nameText) == 0:
            warning = font1_70.render("Don't Leave your name Blank!",
                                                                True, (255,0,0), (255,255,255))
            window.blit(warning, (100, 500))
        
        # Displaying Name Entry
        pygame.draw.rect(window, (175, 0, 175), (50, 350, 650, 100))
        nameEntry = font2_100.render(self.nameText, True, (255, 255, 255))
        window.blit(nameEntry, (60, 335))

        drawKeys() # Draw all keyboard buttons
        
        if hands:  
            hand = hands[0]
            lmList = hand['lmList']
            fingers = detector.fingersUp(hand) 
            # If teach finger is up..
            if fingers[1] == 1:
                # Get X, Y coordinate of the end point of teach finger
                teachX, teachY = lmList[8][0:2] 
                for button in buttonList:
                    x, y = button.pos
                    w, h = button.size
                    # If button key collides with end of teach finger
                    if button.getRect().collidepoint(teachX, teachY):
                        # Display Hover Animation
                        pygame.draw.rect(window, (175, 0, 175), (x, y, w, h))
                        letter = font2_50.render(button.text, True, (255, 255, 255))
                        window.blit(letter, (x + 20, y + 30))
                     
                        self.counter += 1
                        if self.counter == 30: # 1 Second
                            self.counter = 0
                            # Delete last letter if backspace key is clicked
                            if button.text == 'Backspace':
                                self.nameText = self.nameText[:-1]
                            
                            # Enter Game Screen if Enter Key is Clicked
                            elif button.text == 'Enter':
                                if self.nameText != '':
                                    # Change to Splash Scene
                                    self.state = 'splash'
                                    self.splashTime = 0
                            else:
                                if not max:
                                    self.nameText += button.text # Adds Letter
                        break
                            
                else:
                    self.counter = 0
                
                # Display cursor
                window.blit(cursor, (teachX-25, teachY-30))

    def displaySplashScreen(self):
        window.blit(endBG, (0,0))
        pygame.draw.rect(window, (162, 25, 25), (300, 250, 700, 200), border_radius=30)
        splashInfo1 = leaderboard_font.render('Normal Lampion: 5 Points', True, (255,255,255))
        splashInfo2 = leaderboard_font.render('Special Dragon Lampion: 10 Points', True, (255,255,255))
        window.blit(splashInfo1, (450, 300))
        window.blit(splashInfo2, (350, 350))

        self.splashTime += 1
        if self.splashTime == 100:
            # Reset Variables
            self.start = time.time() 
            self.score = 0 
            self.speed = self.initial_speed
            # Reset Initial Position of Lampions
            position_lampions()
            # For Special Lampion Only 
            # Create Spiral Movement
            self.right = True
            # Reset Curtains' Location
            curtainsLeftRect.x = 0
            curtainsRightRect.x = width - 515
            # Change to Game Scene
            self.state = 'game' 
            pygame.mixer.stop()
            transition.play(0)
            gameMusic.play(-1)

    def displayGameScreen(self):
        timeNow = time.time()
        timeLeft = round(self.duration - (timeNow - self.start))

        if timeLeft == 0:
            write_score(self.nameText, self.score)
            # Display End Screen
            self.state = 'end' 
            pygame.mixer.stop()
            transition.play(0)
            endMusic.play(-1)

        else:
            # Display BG
            window.blit(gameBG, (0,0))
            x, y = None, None
            hands = hand_detector()             

            if hands:
                hand = hands[0]
                fingers = detector.fingersUp(hand)
                if fingers[1] == 1: # If teach finger is Up..
                    # Display Dart UI on the end of teach finger
                    x, y = hand['lmList'][8][0:2]
                    window.blit(dart, (x-75, y-75))

            # Move and Display Lampions
            for image, keyRect in zip(lampion_images.values(), lampion_rects.keys()):
                rect = lampion_rects[keyRect] # Get Rect Object
                if keyRect == 'special_lampion_rect':
                    if timeLeft <= self.duration - 5:
                        if x and y:
                            if rect.collidepoint(x, y): # Check for collision
                                # Play SFX and animation
                                boom.play()
                                window.blit(bonus_pop, (x-100, y-75))
                                reset_lampions(keyRect, height*3)
                                # self.speed += self.increase_speed
                                self.score += 10
                        
                        if rect.y < (-rect.height): # Reset Lampion if it's out of frame
                            # So special lampion show up less often
                            reset_lampions(keyRect, height*3)

                        # Create Spiral Movement
                        if rect.y < height:
                            if rect.x == 0:
                                self.right = False
                            elif rect.x == width-120:
                                self.right = True
                            
                            if self.right:
                                rect.x -= 10
                            else:
                                rect.x += 10
                            rect.y -= 2
                        
                        else:
                            # When Out of Frame
                            rect.y -= 10
                        
                        window.blit(image, rect)
                
                else:
                    if x and y:
                        if rect.collidepoint(x, y): # Check for collision
                            # Play SFX and animation
                            pop_sfx.play()
                            window.blit(pop_sprite, (x-100, y-75))
                            reset_lampions(keyRect)
                            self.speed += self.increase_speed
                            self.score += 5
                    
                    if rect.y < (-rect.height): # Reset Lampion if it's out of frame
                        reset_lampions(keyRect)
                
                    rect.y -= self.speed
                    window.blit(image, rect)

            # Display Score, timeLeft and FPS
            FPS = round(clock.get_fps())

            textScore = font2_50.render(f'Score: {self.score}', True, (0,255,0))
            countdown = font2_50.render(f'Time Left: {timeLeft}', True, (0,255,0))
            textFPS = font2_50.render(f'FPS: {FPS}', True, (0,255,0))

            window.blit(textScore, (35, 35))
            window.blit(countdown, (950, 35))
            window.blit(textFPS, (450, 35))

            # Play Curtain Opening Animation Every time Entering Game Screen
            if not curtainsLeftRect.x < -508 or not curtainsRightRect.x > width:
                curtainsLeftRect.x -= 10
                curtainsRightRect.x += 10

                window.blit(curtainsLeft, curtainsLeftRect)
                window.blit(curtainsRight, curtainsRightRect)
        
    def displayEndScreen(self):
        # Display BG and Buttons
        window.blit(endBG, (0,0))
        window.blit(backbtn, backbtn_rect)
        window.blit(quitbtn, quitbtn_rect)

        # Display Text Messages
        back_message = font2_50.render('BACK', True, (255,255,255))
        quit_message = font2_50.render('QUIT', True, (255,255,255))

        window.blit(back_message, (230, 30))
        window.blit(quit_message, (width-320, 30))

        finalScore = font2_100.render(f'Your Score: {self.score}', True, (255,255,255))
        message = font2_100.render(r"TIME'S UP!", True, (255,255,255))

        window.blit(textFrame, (20, 225))
        window.blit(finalScore, (300, 350))
        window.blit(message, (350, 275))

        hands = hand_detector()

        # If Record broken
        if self.scores.size > 0:
            prev_best = self.scores[0]
            if self.score > int(prev_best): 
                # Display Messages
                congrats_message = font1_70.render('Congratz! You have broken a new Record!', 
                                                True, (153, 52, 65), (255, 184, 177))
                prevbest_message = font1_70.render(f'Previous Best Score: {prev_best}',
                                                True, (153, 52, 65), (255, 184, 177))

                window.blit(congrats_message, (50, 485))
                window.blit(prevbest_message, (320, 560))

        # For First Player Only
        else:
            if self.score > 0: 
                # Display Messages
                congrats_message = font1_70.render('Congratz! You have broken a new Record!', 
                                                True, (153, 52, 65), (255, 184, 177))

                window.blit(congrats_message, (50, 485))

        if hands:
            hand = hands[0]
            lmList = hand['lmList']
            fingers = detector.fingersUp(hand) 
            # If teach finger is up..
            if fingers[1] == 1:
                # Get X, Y coordinate of the end point of teach finger
                teachX, teachY = lmList[8][0:2] 
                # Display cursor
                window.blit(cursor, (teachX-25, teachY-30))
                # and if the teach finger collides with the back button..
                if backbtn_rect.collidepoint(teachX, teachY):
                    self.counter += 1
                    if self.counter == 40: # Almost 2 seconds
                        self.counter = 0
                        # Update Leaderboard
                        self.names, self.scores = get_leaderboard()
                        # Change to Home Scene
                        self.state = 'home' 
                        pygame.mixer.stop()
                        homeMusic.play(-1)
                        return
                
                # or the teach finger collides with the quit button..
                elif quitbtn_rect.collidepoint(teachX, teachY):
                    self.counter += 1
                    if self.counter == 40: # Almost 2 seconds
                        self.counter = 0
                        # Closes the Game
                        pygame.quit() 
                        sys.exit()
                
                else:
                    self.counter = 0

    def state_manager(self):
        if self.state == 'home':    
            self.displayHomeScreen()
        elif self.state == 'name':
            self.displayNameScreen()
        elif self.state == 'splash':
            self.displaySplashScreen()
        elif self.state == 'game':
            self.displayGameScreen()
        elif self.state == 'end':
            self.displayEndScreen()            

scene_manager = SceneManager()
homeMusic.play(-1)

# Mainloop  
while True:
    # Get events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Helps change scenes based on state
    scene_manager.state_manager()

    # Update Display
    pygame.display.update()
    # Set FPS
    clock.tick(fps)
