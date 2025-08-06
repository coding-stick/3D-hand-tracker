import pygame, math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np

from tracker2 import HandTracker


# Load obj mesh, v: vertex; 
class Mesh:
    def __init__(self, filename):
        vertices = self.load_mesh(filename)
        self.vertex_count = len(vertices) // 8
        vertices = np.array(vertices, dtype=np.float32)

        # Skip VAO
        # self.vao = glGenVertexArrays(1)
        # glBindVertexArray(self.vao)

        # Create and bind VBO
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Position attribute
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 8 * vertices.itemsize, ctypes.c_void_p(0))

        # no neeed for textures, normals -> vt, vn



    def load_mesh(self, filename):
        v = [] # vertices
        vt = [] # texture coordinates
        vn = [] # normals
        vertices = []
        num =1
        with open(filename, 'r') as file:
            line = file.readline()
            
            

            while line:
                line = line.strip()
                words = line.split()
                if not words or words[0].startswith('#'):
                    line = file.readline()
                    continue
                try:
                    if words[0]=="v":
                        v.append(self.read_vertex_data(words))
                    elif words[0]=="vt":
                        vt.append(self.read_textcoord_data(words))
                    elif words[0]=="vn":
                        vn.append(self.read_normal_data(words))
                    elif words[0]=="f":
                        self.read_face_data(words, v, vt, vn, vertices)
                except Exception as e:
                    print(f"Error on line {num}: {line}")
                    raise e

                line = file.readline()
                num+=1
        return vertices

    def read_vertex_data(self, words):
        return [
            float(words[1]),
            float(words[2]),
            float(words[3])
        ]
    
    def read_textcoord_data(self, words):
        return [
            float(words[1]),
            float(words[2]),
        ]
    
    def read_normal_data(self, words):
        return [
            float(words[1]),
            float(words[2]),
            float(words[3])
        ]
    
    def read_face_data(self,words, v, vt, vn, vertices):
        triangleCount = len(words)-3
        for i in range(triangleCount):
            self.make_corner(words[1], v, vt, vn, vertices)
            self.make_corner(words[i+2], v, vt, vn, vertices)
            self.make_corner(words[i+3], v, vt, vn, vertices)
    
    def make_corner(self, corner_desc, v, vt, vn, vertices):
        v_vt_vn = corner_desc.split('/')

        # Vertex position (always present)
        vi = int(v_vt_vn[0]) - 1
        vertices.extend(v[vi])

        # Texture coordinates (optional)
        if len(v_vt_vn) > 1 and v_vt_vn[1]:
            ti = int(v_vt_vn[1]) - 1
            vertices.extend(vt[ti])
        else:
            vertices.extend([0.0, 0.0])  # default tex coords

        # Normals (optional)
        if len(v_vt_vn) > 2 and v_vt_vn[2]:
            ni = int(v_vt_vn[2]) - 1
            vertices.extend(vn[ni])
        else:
            vertices.extend([0.0, 0.0, 0.0])  # default normal


    def destroy(self):
        glDeleteBuffers(1, [self.vbo])




def draw_axes(length=2.0):
    glLineWidth(2.0)
    glBegin(GL_LINES)

    # X axis - Red
    glColor3f(1, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(length, 0, 0)

    # Y axis - Green
    glColor3f(0, 1, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, length, 0)

    # Z axis - Blue
    glColor3f(0, 0, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, length)

    glEnd()



def draw_grid(size=10, spacing=1):
    glColor3f(0.5, 0.5, 0.5)
    glLineWidth(1.0)
    glBegin(GL_LINES)

    for i in range(-size, size+1):
        # Lines parallel to X axis
        glVertex3f(-size * spacing, 0, i * spacing)
        glVertex3f(size * spacing, 0, i * spacing)
        # Lines parallel to Z axis
        glVertex3f(i * spacing, 0, -size * spacing)
        glVertex3f(i * spacing, 0, size * spacing)

    glEnd()



def main():

    

    #init
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    testMesh = Mesh("monkey.obj")
    
    #change this if u want orthographic / perspective view
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0]/display[1]), 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

    rMode = GL_LINE
    glPolygonMode(GL_FRONT_AND_BACK, rMode) # put GL_FILL for solid rendering, GL_LINE for wireframe

    # Spherical coordinates
    radius = 10.0
    theta = math.pi / 2   # horizontal angle (left-right)
    phi = 0               # vertical angle (up-down)

    clock = pygame.time.Clock()



    # tracking stuff

    tracker = HandTracker()
    tracker.start()

    while True:
        zoom = tracker.state['zoom']
        strafe_lr = tracker.state['strafe_lr']
        strafe_ud = tracker.state['strafe_ud']

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return

        # keyboard controls
        keys = pygame.key.get_pressed()
        if keys[K_a]:
            theta -= 0.02
        if keys[K_d]:
            theta += 0.02
        if keys[K_w]:
            phi += 0.02
            phi = min(phi, math.pi / 2 - 0.01)  # avoid looking straight up
        if keys[K_s]:
            phi -= 0.02
            phi = max(phi, -math.pi / 2 + 0.01) # avoid looking straight down
        if keys[K_q]:
            radius -= 0.2
            radius = max(1.0, radius)
        if keys[K_e]:
            radius += 0.2
        if keys[K_r]:
            radius = 10.0
            theta = math.pi / 2   # horizontal angle (left-right)
            phi = 0               # vertical angle (up-down)
        if keys[K_m]:
            if rMode == GL_LINE:
                
                rMode = GL_FILL
                glPolygonMode(GL_FRONT_AND_BACK, rMode)
            else:
                rMode = GL_LINE
                glPolygonMode(GL_FRONT_AND_BACK, rMode)
            


        # hand controls
        
        if zoom==0:
            radius = 10
        else:
            radius = zoom*2
        theta +=strafe_lr
        phi += strafe_ud

    
        # Convert spherical to Cartesian
        cam_x = radius * math.cos(phi) * math.sin(theta)
        cam_y = radius * math.sin(phi)
        cam_z = radius * math.cos(phi) * math.cos(theta)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(
            cam_x, cam_y, cam_z,  # Camera position
            0, 0, 0,              # Looking at origin
            0, 1, 0               # Up vector
        )

        glClearColor(0.2, 0.2, 0.2, 1) # background color

        glColor3f(1.0, 1.0, 0.5) # drawing color

        # draw mesh
        glBindBuffer(GL_ARRAY_BUFFER, testMesh.vbo)
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 8 * 4, ctypes.c_void_p(0))
        glDrawArrays(GL_TRIANGLES, 0, testMesh.vertex_count)

        draw_axes(20)
        draw_grid()

        pygame.display.flip()
        clock.tick(60)

main()
