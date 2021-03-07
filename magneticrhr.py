import ipywidgets as widgets
import ipywidgets
from IPython.display import display
import random
import numpy as np
import collections
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'widget')
#%matplotlib widget

class MagneticRHR(widgets.VBox):
    '''An ipywidget for students to test their knowledge of the magnetic force
    right-hand-rule in Jupyter notebooks.  Calling the class will
    start the self-test, which will run until the notebook is quit.

    Only the simplest cases are currently handled. I.e., magnetic
    fields and particle velocities are along the x-, y-, or z-axes.

    '''
    def __init__(self, charge_type):
        '''Initialize the test.  It is automatically ready to be displayed.
        Args:
            charge_type: 
                (str) 'particle' or 'current'.  Charges for 
                'particle' can be positive or negative.  'current' is 
                always in the direction of the current.    
        '''
        self.charge_type = charge_type
        
        if charge_type not in ['particle', 'current']:
            raise ValueError('`charge_type` must be "particle" or "current"')
        
        self.directions = collections.OrderedDict(
            {( 0, 0, 0):'None',
             ( 1, 0, 0):'Right', 
             (-1, 0, 0):'Left', 
             ( 0, 1, 0):'Up', 
             ( 0,-1, 0):'Down',
             ( 0, 0, 1):'Out of Page',
             ( 0, 0, -1):'Into Page'})

        # Dropdown menu to select what the student is looking for
        self.unknown_choice = 'random'
        self.unknown_choices = ['random', self.charge_type, "force", "magnetic field"]
        self.unknown_widget_dropdown = widgets.Dropdown(
            options=self.unknown_choices,
            value='random',
            description='',
            style = {'description_width': 'initial'},
            disabled=False)
        self.unknown_widget = widgets.VBox([
            widgets.HTML(
                value='Use the magnetic force right-hand-rule to find the direction of the '),
            self.unknown_widget_dropdown])
        self.unknown_widget_dropdown.observe(self._set_unknown, 'value')
        
        # Dropdown menu to select the values from. Added a dummy answer as the starting point.
        self.direction_widget = widgets.Dropdown(
            options=['']+list(self.directions.values()),
            value=None,
            description='Direction:',
            disabled=False)
        # callback for when a new value is selected.
        self.direction_widget.observe(self._guess, 'value')

        # display of the magnetic field plot
        self.display_widget = widgets.Output(layout = ipywidgets.Layout(width='500px'))
        with self.display_widget:
            self.fig, self.ax = plt.subplots(constrained_layout=True, figsize=(5, 5))
            self.ax.set_aspect('equal')

        # output widget to tell the student if they are right or wrong
        self.output_widget = widgets.Output()

        # get the next example
        self.next_widget = widgets.Button(
            description='Next',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Get next problem',
            #icon='arrow-right'
        )
        # callback function
        self.next_widget.on_click(self.next)

        # stack the widgets and display the first problem
        super().__init__([
            self.unknown_widget,
            self.display_widget, 
            self.direction_widget, 
            self.output_widget, 
            self.next_widget])
        self.display_problem()
        
    def next(self, button):
        '''
        Generate the next problem
        '''
        self.display_problem()
        
    def display_problem(self):
        '''
        Generates and displays the next problem
        '''
        charge = 1
        if self.charge_type == 'particle':
            charge = random.choice([-1,1])
            
        # local copy of the unknown choice so it can be selected from random if necessary
        if self.unknown_choice == 'random':
            unknown_choice = random.choice(self.unknown_choices[1:])
        else:
            unknown_choice = self.unknown_choice
            
        # make sure that if the force is being displayed, it is not 'none'. 
        # For no force, there are multiple correct answers in this case.
        while True:
            # generate a random B-field, particle velocity and charge from
            # the fixed options.  The first direction is 'None' so ignore
            # it.
            B_field = np.array(random.choice(list(self.directions.keys())[1:]))
            velocity = np.array(random.choice(list(self.directions.keys())[1:]))
            # calculate the force
            force = charge*np.cross(velocity, B_field)
            if unknown_choice == 'force' or self.directions[tuple(force)] != 'None':
                break
        
        self.direction_widget.value=None
        
        # clear the previous response to the student
        self.output_widget.clear_output()
        with self.output_widget:
            print('\n')


        # clear and recreate the plot.  `wait=True` is required to avoid flickering.
        self.display_widget.clear_output(wait=True)
        self.ax.clear()
        self.ax.axis('off')
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
                
        # set the correct answer for the unknown value and display the knowns.
        if unknown_choice == 'force':
            self.correct = self.directions[tuple(force)]
            self._draw_B_field(B_field)
            self._draw_particle_current_force(charge, velocity, force=False)
        elif unknown_choice == 'magnetic field':
            self.correct = self.directions[tuple(B_field)]
            self._draw_particle_current_force(charge, velocity, force=False)
            self._draw_particle_current_force(charge, force, force=True)
        elif unknown_choice == self.charge_type:
            self.correct = self.directions[tuple(velocity)]
            self._draw_B_field(B_field)
            self._draw_particle_current_force(charge, force, force=True)
        
        self.ax.legend()
        # display the plot
        with self.display_widget:
            # print(B_field, velocity, charge, force)
            display(self.ax.figure)

    def _draw_particle_current_force(self, charge, vector, force):
        '''
        Draws a vector for the particle/current velocity/force vector and label
        
        Args:
            charge:
                (-1 or 1)
            force:
                (list of ints) force vector
        '''
        if force:
            color='C2'
            label = 'Force on'
            va='bottom'
        else:
            color='C0'
            label = 'Direction of'
            va='top'
        
        if self.charge_type == 'particle':
            if charge >0:
                label += ' Positive Particle'
            else:
                label += ' Negative Particle'
        else:
            label += ' Current'

        # into and out of the page require special treatment since we
        # use special vector symbols in these cases
        if np.sum(np.abs(vector[:2])) > 0:
            self.ax.quiver(
                *list(-vector[:2]/2), 
                *list(vector[:2]), 
                color=color, 
                scale=1, scale_units='xy', label=label)
            rotation='horizontal'
            if vector[1]!=0:
                rotation='vertical'
        elif vector[2] < 0:
            self.ax.scatter([0],[0], marker='x', s=200,  facecolors=color, edgecolors = color, label=label)
        elif vector[2] > 0:
            self.ax.scatter([0],[0], marker=r'$\bigodot$', s=200, 
                            facecolors=color, edgecolors=color, label=label)
            
    def _draw_B_field(self, direction):
        '''
        Draws the B-field vector
        
        Args:
            direction:
                (list of ints) direction vector
        '''
        color='C1'
        label = 'Magnetic field'
        nvectors = 11

        # into and out of the page require special treatment since we
        # use special vector symbols in these cases. Also, up/down and
        # left/right need special treatment

        if direction[0] != 0:
            self.ax.quiver(
                np.full([nvectors], -direction[0]), 
                np.linspace(-1, 1, nvectors), 
                np.full([nvectors], direction[0]), 
                np.zeros([nvectors]),
                color=color, 
                scale=0.5, scale_units='x', label=label)
        elif direction[1] != 0:
            self.ax.quiver(
                np.linspace(-1, 1, nvectors), 
                np.full([nvectors], -direction[1]), 
                np.zeros([nvectors]),
                np.full([nvectors], direction[1]), 
                color=color, 
                scale=0.5, scale_units='y', label=label)
        elif direction[2] < 0:
            X, Y = np.meshgrid(np.linspace(-1, 1, nvectors), np.linspace(-1, 1, nvectors))
            self.ax.scatter(X,Y, marker='x', s=200, facecolors = color,edgecolors=color, label=label)
        elif direction[2] > 0:
            X, Y = np.meshgrid(np.linspace(-1, 1, nvectors), np.linspace(-1, 1, nvectors))
            self.ax.scatter(X, Y, marker=r'$\bigodot$', s=200, 
                            facecolors=color, edgecolors=color, label=label)


    def _guess(self, change):
        '''Update the student and let them know if they are right or not.

        '''
        self.output_widget.clear_output()
        with self.output_widget:
            if change['new']==self.correct:
                print('Correct!')
            else:
                print('Try again.')

    def _set_unknown(self, unknown_choice):
        '''Record the user's choice of what to look for and generate a new problem.
        '''
        self.unknown_choice = unknown_choice['new']
        self.next(None)