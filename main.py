from copyreg import pickle
import pygame
import os, random, sys
import neat, math
import pickle

pygame.init()
print("Initialized PYGAME")

game_speed = 20
all_time_highest = 0

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1800
TOP_RIGHT = 1600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUNNNING_BLACK = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1Black.png")),
            pygame.image.load(os.path.join("Assets/Dino", "DinoRun2Black.png"))]
RUNNNING_WHITE = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1White.png")),
            pygame.image.load(os.path.join("Assets/Dino", "DinoRun2White.png"))]

JUMPING_BLACK = pygame.image.load(os.path.join("Assets/Dino", "DinoJumpBlack.png"))
JUMPING_WHITE = pygame.image.load(os.path.join("Assets/Dino", "DinoJumpWhite.png"))

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

hundread_point_sound = pygame.mixer.Sound(os.path.join("Assets/Sounds", "100points.mp3"))
lost_sound = pygame.mixer.Sound(os.path.join("Assets/Sounds", "lost.mp3"))
jump_sound = pygame.mixer.Sound(os.path.join("Assets/Sounds", "jump.mp3"))


DARK = (0, 0, 0)
LIGHT = (255, 255, 255)

MODE = "light"
BG_COLOR = LIGHT

GAME_FONT = pygame.font.SysFont("comicsans", 30)
GAME_OVER_FONT = pygame.font.Font("Assets/Fonts/game_over.ttf", 500)

SMALL_CACTUS_BLACK = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1Black.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2Black.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3Black.png"))]

SMALL_CACTUS_WHITE = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1White.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2White.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3White.png"))]

LARGE_CACTUS_BLACK = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1Black.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2Black.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3Black.png"))]

LARGE_CACTUS_WHITE = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1White.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2White.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3White.png"))]

OUTLINE_CONSTANT = 2

class Obstacle:
    def __init__(self, image, number_of_cacti):
        self.image = image
        self.type = number_of_cacti
        self.rect = pygame.Rect(SCREEN_WIDTH, 0, self.image[self.type].get_width() - OUTLINE_CONSTANT, self.image[self.type].get_height() - OUTLINE_CONSTANT)
        if MODE == "light":
            self.box_color = DARK
        else:
            self.box_color = LIGHT

    def update(self):
        self.rect.x -= game_speed
        print(f"rectX: {self.rect.x} rectWidth: {self.rect.width}")
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)
        pygame.draw.rect(SCREEN, self.box_color, self.rect, 2)


class SmallCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 300

class Dinosaur:
    X_POS = 80
    Y_POS = 310
    JUMP_VEL = 8.5
    
    def __init__(self, img=RUNNNING_BLACK[0]):
        self.image = img
        self.dino_run = True
        self.dino_jump = False
        self.jump_vel = self.JUMP_VEL
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, self.image.get_width() - OUTLINE_CONSTANT, self.image.get_height() - OUTLINE_CONSTANT)
        self.box_color = (random.randint(10, 245), random.randint(10, 245), random.randint(10, 245))
        self.step_index = 0
        
    def update(self):
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()
        if self.step_index >= 10:
            self.step_index = 0
    
    def jump(self):
        # negative jump velocity goes up
        # positive jump velocity goes down
        if MODE == "light":
            self.image = JUMPING_BLACK
        elif MODE == "dark":
            self.image = JUMPING_WHITE
        self.adj_jump_speed()
        if self.dino_jump:
            self.rect.y -= self.jump_vel * 4 # change the y axis of the rectangle of our dino
            self.jump_vel -= self.jump_decel
        if self.jump_vel <= -self.JUMP_VEL:
            self.dino_jump = False
            self.dino_run = True
            self.jump_vel = self.JUMP_VEL
    
    def run(self):
        if MODE == "light":
            self.image = RUNNNING_BLACK[self.step_index // 5] # change an image every 5 counts of the step_index
        elif MODE == "dark":
            self.image = RUNNNING_WHITE[self.step_index // 5] # change an image every 5 counts of the step_index
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.step_index += 1
    
    def draw(self, SCREEN):
        SCREEN.blit(self.image, self.rect)
        pygame.draw.rect(SCREEN, self.box_color, self.rect, 2)
        for obstacle in obstacles:
            pygame.draw.line(SCREEN, self.box_color, (self.rect.x + 54, self.rect.y + 12), obstacle.rect.midleft, 2) # 54 and 12 are the offsets for the dinosaurs eye
    
    def adj_jump_speed(self):
        # self.JUMP_VEL = (game_speed / 2.35)
        # print(f"JUMP_VEL: {self.JUMP_VEL}")
        # self.jump_vel = - (game_speed / 2.35)
        self.jump_decel = 0.8 #(self.jump_vel*4)**2 / 1445
        # print(f"jump_vel: {self.jump_vel}")
        # print(f"jump_decel: {self.jump_decel}")

    
def remove(index):
    dinosaurs.pop(index)    
    ge.pop(index)
    nets.pop(index)

def distance(pos_a, pos_b, number_of_cactii):
    cactii_k = 10
    distance_k = 1.2
    dx = pos_a[0]-pos_b[0]
    dy = pos_a[1]-pos_b[1]
    distance = math.sqrt(dx**2 + dy**2) - (game_speed * distance_k) + (number_of_cactii * cactii_k)
    if distance < 0:
        distance = 0
    print(f"Distance to next obstacle: {distance}")
    return distance

def generate_obstacle(cactus_index, color, number_of_cactii):
    if cactus_index == 0:
        if color == "dark":
            obstacles.append(SmallCactus(SMALL_CACTUS_BLACK, number_of_cactii))
        elif color == "light":
            obstacles.append(SmallCactus(SMALL_CACTUS_WHITE, number_of_cactii))
    elif cactus_index == 1:
        if color == "dark":
            obstacles.append(LargeCactus(LARGE_CACTUS_BLACK, number_of_cactii))
        elif color == "light":
            obstacles.append(LargeCactus(LARGE_CACTUS_WHITE, number_of_cactii))

def main(genomes, config, replaying=False):
    global game_speed, x_pos_bg, y_pos_bg, obstacles, dinosaurs, ge, nets, population, points, all_time_highest, MODE, GAME_OVER
    points = 0
        
    clock = pygame.time.Clock()

    # create many dinosaurs for the AI to play with
    dinosaurs = []    
    obstacles = []
    ge = []
    nets = []
    
    x_pos_bg = 0
    y_pos_bg = 380
    
    game_speed = 20
    
    for genomed_id, genome in genomes:
        dinosaurs.append(Dinosaur())
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    def stats():
        global dinosaurs, game_speed, ge, points, all_time_highest, MODE, BG_COLOR, GAME_OVER

        # Scoring
        points += 1
        if points % 100 == 0:
            pygame.mixer.Sound.play(hundread_point_sound)
            pygame.mixer.music.stop()
            game_speed += 1
            
        # every 700 score change modes
        if points % 700 == 0 and points != 0:
            if MODE == "light":
                MODE = "dark"
                BG_COLOR = DARK
            elif MODE == "dark":
                MODE = "light"
                BG_COLOR = LIGHT
        else:
            SCREEN.fill(BG_COLOR)
        
        text_color = (255 - abs(BG_COLOR[0]), abs(255 - BG_COLOR[1]), abs(255 - BG_COLOR[2])) # invert when the bg color inverts
        
        score = GAME_FONT.render(f'Score:  {str(points)}', True, text_color)
        SCREEN.blit(score, (TOP_RIGHT, 30))

        if points > all_time_highest:
            all_time_highest = points
        
        speed = GAME_FONT.render(f'Game Speed:  {str(game_speed)}', True, text_color)
        SCREEN.blit(speed, (TOP_RIGHT, 60))
        
        highest = GAME_FONT.render(f'All Time Highest:  {str(all_time_highest)}', True, text_color)
        SCREEN.blit(highest, (TOP_RIGHT, 90))
        
        if not replaying:
            alive_num = GAME_FONT.render(f'Dinosaurs Alive:  {str(len(dinosaurs))}', True, text_color)
            SCREEN.blit(alive_num, (TOP_RIGHT, 120))
        
            gen = GAME_FONT.render(f'Generation:  {population.generation+1}', True, text_color)
            SCREEN.blit(gen, (TOP_RIGHT, 150))
        
        GAME_OVER = GAME_OVER_FONT.render("GAME OVER", True, text_color)
        
    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed
    
    game_over = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not game_over:
            stats()
            background()
            
            if len(obstacles) == 0:
                size = random.randint(0, 1)
                number_of_cactii = random.randint(0, 2)
                generate_obstacle(size, MODE, number_of_cactii)            

            for dinosaur in dinosaurs:
                dinosaur.update()
                dinosaur.draw(SCREEN)
            
            if len(dinosaurs) == 0:
                break
            
            for obstacle in obstacles:
                obstacle.draw(SCREEN)
                obstacle.update()
                for i, dinosaur in enumerate(dinosaurs):
                    output = nets[i].activate((dinosaur.rect.y, 
                                            distance((dinosaur.rect.x, dinosaur.rect.y),
                                                obstacle.rect.midleft, number_of_cactii)))
                    if dinosaur.rect.colliderect(obstacle.rect):
                        ge[i].fitness = points
                        remove(i)
                        if replaying:
                            game_over = True
                    elif output[0] > 0.5 and dinosaur.rect.y == dinosaur.Y_POS: # checks if not jumping already (in the air)
                        pygame.mixer.Sound.play(jump_sound)
                        pygame.mixer.music.stop()
                        dinosaur.dino_jump = True
                        dinosaur.dino_run = False        
        else:
            GAME_OVER_RECT = GAME_OVER.get_rect(center=pygame.display.get_surface().get_rect().center)
            SCREEN.blit(GAME_OVER, GAME_OVER_RECT)
        clock.tick(30)
        pygame.display.update()

def replay_genome(config_path, genome_path):
    global all_time_highest
    
    # Load requried NEAT config
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Unpickle saved winner
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    # Convert loaded genome into required data structure
    genomes = [(1, genome)]

    all_time_highest = genome.fitness

    # Call main with the only loaded genome
    main(genomes, config, replaying=True)        

# NEAT ALGO
def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome, 
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    
    global population
    choice = input("Run NEAT evolution from the beggining or load the best model(1,2): ")
    if choice == "1":
        population = neat.Population(config)
        number_of_generations = int(input("Number of generations: "))
        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        population.add_reporter(stats)
        population.run(main, number_of_generations)
        best_genome = population.best_genome
        with open(f"Models/genome_{best_genome.fitness}.pkl", "wb") as f:
            pickle.dump(best_genome, f, protocol=pickle.HIGHEST_PROTOCOL)
    elif choice == "2":
        # make a menu with all pickle files in the folder
        files = os.listdir("Models")
        files.sort()
        for i, file in enumerate(files):
            print(f"{i+1}. {file}")
        choice = int(input("Choose a file: "))
        genome_path = f"Models/{files[choice-1]}"
        replay_genome(config_path, genome_path)
    else:
        print("Invalid choice")
        exit()
    
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'Config/config.txt')
    run(config_path)