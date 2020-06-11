import ipywidgets as widgets
import ipywidgets
from IPython.display import display
import random
import numpy as np
import collections
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'widget')
#%matplotlib widget

class MagneticRHR:
    def __init__(self):
        self.directions = collections.OrderedDict(
            {( 0, 0, 0):'None',
             ( 1, 0, 0):'Right', 
             (-1, 0, 0):'Left', 
             ( 0, 1, 0):'Up', 
             ( 0,-1, 0):'Down',
             ( 0, 0, 1):'Out of Page',
             ( 0, 0, -1):'Into Page'})
        
        self.direction_widget = widgets.Dropdown(
            options=['']+list(self.directions.values()),
            value=None,
            description='Direction:',
            disabled=False)
        self.direction_widget.observe(self._guess, 'value')
        
        self.display_widget = widgets.Output(layout = ipywidgets.Layout(width='50%'))
        with self.display_widget:
            self.fig, self.ax = plt.subplots(constrained_layout=True, figsize=(5, 5))
            self.ax.set_aspect('equal')

        self.output_widget = widgets.Output()
        
        self.next_widget = widgets.Button(
            description='Next',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Get next problem',
            icon='check' )
        self.next_widget.on_click(self.next)

        display(widgets.VBox([self.display_widget, self.direction_widget, self.output_widget, self.next_widget]))
        self.display_problem()
        
    def next(self, button):    
        self.display_problem()
        
    def display_problem(self):
        B_field = np.array(random.choice(list(self.directions.keys())[1:]))
        velocity = np.array(random.choice(list(self.directions.keys())[1:]))
        charge = random.choice([-1,1])
        force = tuple(charge*np.cross(velocity, B_field))
        self.correct = self.directions[force]
        self.direction_widget.value=None
        
        self.output_widget.clear_output()
        with self.output_widget:
            print('\n')

        self.display_widget.clear_output(wait=True)
        
        self.ax.clear()
        self.ax.axis('off')

            
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)

        self._draw_B_field(B_field)
        self._draw_particle(charge, velocity)

        with self.display_widget:
            # print(B_field, velocity, charge, force)
            display(self.ax.figure)

    def _draw_particle(self, charge, velocity):
        color='C0'
        if charge >0:
            particle_label = 'Positive particle'
        else:
            particle_label = 'Negative particle'


        if np.sum(np.abs(velocity[:2])) > 0:
            self.ax.quiver(
                *list(-velocity[:2]/2), 
                *list(velocity[:2]), 
                color=color, 
                scale=1, scale_units='xy')
            rotation='horizontal'
            if velocity[1]!=0:
                rotation='vertical'
            self.ax.text(*list(velocity[:2][::-1]*0.15), particle_label, 
                         c=color, ha='center', va='top',
                        rotation=rotation, rotation_mode='anchor')
        elif velocity[2] < 0:
            self.ax.scatter([0],[0], marker='x', s=200,  edgecolors = color)
            self.ax.text(0,0.1, particle_label, c=color, ha='center', va='top')
        elif velocity[2] > 0:
            self.ax.scatter([0],[0], marker='o', s=200, 
                            facecolors='none', edgecolors=color)
            self.ax.scatter([0],[0], marker='o', s=40,  edgecolors = color)
            self.ax.text(0,.15, particle_label, c=color, ha='center', va='top')

    def _draw_B_field(self, direction):
        color='C1'
        label = 'Magnetic field'
        nvectors = 11
        if direction[0] != 0:
            self.ax.quiver(
                np.full([nvectors], -direction[0]), 
                np.linspace(-1, 1, nvectors), 
                np.full([nvectors], direction[0]), 
                np.zeros([nvectors]),
                color=color, 
                scale=0.5, scale_units='x')
            self.ax.text(0, 1 - 1/nvectors, label, 
                         c=color, ha='center', va='center')
        elif direction[1] != 0:
            self.ax.quiver(
                np.linspace(-1, 1, nvectors), 
                np.full([nvectors], -direction[1]), 
                np.zeros([nvectors]),
                np.full([nvectors], direction[1]), 
                color=color, 
                scale=0.5, scale_units='y')
            self.ax.text(-1 + 1/nvectors, 0, label, 
                         c=color, ha='center', va='center',
                         rotation='vertical', rotation_mode='anchor')
        elif direction[2] < 0:
            X, Y = np.meshgrid(np.linspace(-1, 1, nvectors), np.linspace(-1, 1, nvectors))
            self.ax.scatter(X,Y, marker='x', s=200, facecolors = color,edgecolors=color)
            self.ax.text(0,1 - 1/nvectors, label, c=color, ha='center', va='center')
        elif direction[2] > 0:
            X, Y = np.meshgrid(np.linspace(-1, 1, nvectors), np.linspace(-1, 1, nvectors))
            self.ax.scatter(X, Y, marker='o', s=200, 
                            facecolors='none', edgecolors=color)
            self.ax.scatter(X, Y, marker='o', s=40, facecolors = color, edgecolors = color)
            self.ax.text(0, 1 - 1/nvectors, label, c=color, ha='center', va='top')


    def _guess(self, change):
        self.output_widget.clear_output()
        with self.output_widget:
            if change['new']==self.correct:
                print('Correct!')
            else:
                print('Try again.')
