# implementation of Asteroids
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
started = False

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
#nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.s2014.png")
nebula_image = simplegui.load_image("https://raw.githubusercontent.com/BegoUrsus/asteroids/master/fondo3.png");

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
#splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")
splash_image = simplegui.load_image("https://raw.githubusercontent.com/BegoUrsus/asteroids/master/splash2.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
# .ogg versions of sounds are also available, just replace .mp3 by .ogg
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


# Ship class
class Ship:

    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust:
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0], self.image_center[1]] , self.image_size,
                              self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                              self.pos, self.image_size, self.angle)
        # canvas.draw_circle(self.pos, self.radius, 1, "White", "White")

    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT

        # update velocity
        if self.thrust:
            acc = angle_to_vector(self.angle)
            self.vel[0] += acc[0] * .1
            self.vel[1] += acc[1] * .1
            
        self.vel[0] *= .99
        self.vel[1] *= .99

    def set_thrust(self, on):
        self.thrust = on
        
        # extra: stop trusting and playing thrust sound if the game is over
        if not started:
            self.thrust = False
            ship_thrust_sound.pause()
            return

        if self.thrust: #on:
            ship_thrust_sound.rewind()
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.pause()
       
    def increment_angle_vel(self):
        self.angle_vel += .05
        
    def decrement_angle_vel(self):
        self.angle_vel -= .05
        
    def shoot(self):
        # p3.2 Modify your shoot method of my_ship to create a new missile
        # and add it to the missile_group.
        if not started:
            #extra: avoid shooting if the game is over
            return
        global missile_group
        forward = angle_to_vector(self.angle)
        missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
        missile_vel = [self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
        a_missile = Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile) 
        
    # p2.1 returns ship's position
    def get_position(self):
        return self.pos
    
    # p2.1 returns ship's radius
    def get_radius(self):
        return self.radius
        
    # extra, initializes ship's parameters
    def reset(self, pos, vel, angle):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.set_thrust(False)
        self.angle = angle
        self.angle_vel = 0


    
    
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        # bonus 1: If the sprite is animated, choose the correct tile in the image 
        # based on the age. The image is tiled horizontally. 
        # If self.animated is False, it should continue to draw the sprite as before
        center = self.image_center[:]
        if self.animated:
            center[0] = self.image_center[0] + (self.image_size[0] * self.age)               
        canvas.draw_image(self.image, center, self.image_size,
                          self.pos, self.image_size, self.angle)

    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        
        # p3.3 increment the age of the sprite every time update is called
        self.age += 1
        # p3.3 If the age is greater than or equal to the lifespan of the sprite, 
        # then we want to remove it. 
        # So, return False (meaning we want to keep it) if the age is less than the lifespan 
        # and True (meaning we want to remove it) otherwise
        return self.age >= self.lifespan
        
    # p2.1 returns sprite's position
    def get_position(self):
        return self.pos
    
    # p2.1 returns sprite's radius
    def get_radius(self):
        return self.radius

       
    # p2.1 Add collide method to the Sprite class. 
    # This should take an other_object as an argument and 
    # return True if there is a collision or False otherwise. 
    # Collisions can be detected using the radius of the two objects. 
    def collide(self, other_object):
        other_pos = other_object.get_position()
        other_radius = other_object.get_radius()
        return (dist(self.pos, other_pos) <= self.radius + other_radius)
    
# p2.2 group_collide helper function. 
# Takes a set group and an a sprite other_object and check 
# for collisions between other_object and elements of the group. 
# If there is a collision, the colliding object should be removed from the group. 
# Returns True or False depending on whether there was a collision. 
def group_collide(set_group, other_object):
    global explosion_group
    was_collision = False
    # To avoid removing an object from a set that is being iterated over, 
    # we iterate over a copy of the set created via set(group)
    for element in set(set_group):
        if element.collide(other_object):
            set_group.remove(element)
            was_collision = True
            # bonus 3: if there is a collision, create a new explosion 
            # and add it to the explosion_group. 
            a_explosion = Sprite(element.pos,
                                 element.vel,
                                 element.angle,
                                 element.angle_vel,
                                 explosion_image,
                                 explosion_info,
                                 explosion_sound)
            explosion_group.add(a_explosion)
            
    return was_collision
  
# p4.1 group_group_collide takes two groups of objects as input. 
# It iterates through the elements of a copy of the first group 
# and then call group_collide with each of these elements on the second group. 
# It returns the number of elements in the first group that collide 
# with the second group as well as delete these elements in the first group. 
# We use the discard method instead of remove as it doesn't raise an
# error if the element is not in the set
def group_group_collide(group1, group2):
    collisions = 0
    for element1 in set(group1):
        if group_collide(group2, element1):
            group1.discard(element1) 
            collisions += 1
    return collisions
        
# key handlers to control ship   
def keydown(key):
    if not started: # do nothing if game is over
        return
    if key == simplegui.KEY_MAP['left']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(True)
    elif key == simplegui.KEY_MAP['space']:
        my_ship.shoot()
        
def keyup(key):
    if not started: # do nothing if game is over
        return
    if key == simplegui.KEY_MAP['left']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(False)
        
# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started
    global lives, score
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        #p5.2 Initialize lives and score. Play/restart the background music
        lives = 3
        score = 0
        soundtrack.play()

# p1.3 calls update and draw for every sprite in the group
def process_sprite_group(group, canvas):
    # we iterate over a copy of the group, to avoid problems when removing items from it
    for sprite in set(group):
        # p3.4: if the update of the sprite returns true, we must remove it form the group
        # (its age is >= than its lifespan)
        if sprite.update():
            group.remove(sprite)
        else:
            # if we don't remove the sprite, we draw it
            sprite.draw(canvas)
            
def draw(canvas):
    global time, started
    global lives, score
    global my_ship, rock_group, missile_group, explosion_group
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    
    # p2.3 determine if the ship hit any of the rocks. 
    # If so, decrease the number of lives by one. 
    # Note that you could have negative lives at this point. Don't worry about that yet.
    if group_collide(rock_group, my_ship):
        lives -= 1
        
    # p5.1: if the number of lives becomes 0, the game is reset and the splash screen appears. 
    # In particular, set the flag started to False, destroy all rocks 
    if lives <= 0:
        started = False
        rock_group = set()	# p1.1: Initialize the rock group to an empty set
        missile_group = set()	# p3.1: Initialize the missile group to an empty set.
        explosion_group = set()
        my_ship.reset([WIDTH / 2, HEIGHT / 2], [0, 0], 0) # extra
        soundtrack.rewind() # p5.5 stop background music
    
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())
        return
    
    # p4.2 Call group_group_collide in the draw handler to detect missile/rock collisions. 
    # Increment the score by the number of missile collisions
    score += group_group_collide(missile_group, rock_group)
    
    # draw and update ship
    my_ship.draw(canvas)
    my_ship.update()
    
    # draw and update sprites
    process_sprite_group(rock_group, canvas) # p1.4 call process_sprite_group on rock_group
    process_sprite_group(missile_group, canvas) # p3.2 call process_sprite_group on missile_group
    process_sprite_group(explosion_group, canvas) #bonus 4: call process_sprite_group to process explosion_group

    # draw UI
    canvas.draw_text("Lives", [50, 50], 22, "White")
    canvas.draw_text("Score", [680, 50], 22, "White")
    canvas.draw_text(str(lives), [50, 80], 22, "White")
    canvas.draw_text(str(score), [680, 80], 22, "White")


# timer handler that spawns a rock    
def rock_spawner():
    global rock_group
    
    # p5.1 if game is over, prevent any more rocks for spawning until the game is restarted
    if not started:
        return
    
    # p1.2: limit the total number of rocks to 12
    if len(rock_group) >= 12:
        return
    
    # p1.1: create a new rock (an instance of a Sprite object) 
    # and add it to rock_group. 
    # Set random position, velocity and ang. vel. to new rock
    rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
    # p5.3: make rock position at least 150px away from ship to avoid collision 
    # when rock shows up
    while dist(rock_pos, my_ship.get_position()) < 100:
        rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]    
    rock_vel = [random.random() * .6 - .3, random.random() * .6 - .3]
    # p5.3 Increase the velocity of rocks based on the score 
    # to make game play more difficult as the game progresses.
    score_factor = (score / 5) + 1 #(to avoid zero)
    rock_vel[0] *= score_factor
    rock_vel[1] *= score_factor
    rock_avel = random.random() * .2 - .1
    a_rock = Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image, asteroid_info)
    rock_group.add(a_rock)
    
# initialize stuff
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
rock_group = set()	# p1.1: Initialize the rock group to an empty set
missile_group = set()	# p3.1: Initialize the missile group to an empty set
explosion_group = set()	# bonus 2: Initialize the explosion_group to an empty set


# register handlers
frame.set_keyup_handler(keyup)
frame.set_keydown_handler(keydown)
frame.set_mouseclick_handler(click)
frame.set_draw_handler(draw)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
