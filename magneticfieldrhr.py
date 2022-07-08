import ipywidgets as widgets
from IPython.display import display
import random
import os.path
import ipyevents

class WidgetList(widgets.VBox):
    def __init__(self, widgets):
        super().__init__(widgets)

        
class MagneticFieldRHR(widgets.VBox):
    '''An ipywidget for students to test their knowledge of the magnetic field
    right-hand-rules in Jupyter notebooks.  Calling the class will
    start the self-test, which will run until the notebook is quit.

    Only the simplest cases are currently handled. I.e., magnetic
    fields of currents along the x-, y-, or z-axes and magnetic fields
    of loops in the xy, xz, and yz planes.

    '''
    def __init__(self, current_type):

        '''Initialize the test.  It is automatically ready to be displayed.
        Args:
            current_type: 
                (str) 'straight' or 'loop'.
        '''
        self.current_type = current_type
        self.width = 300
        self.n_answer_col = 2
        
        if current_type not in ['straight', 'loop']:
            raise ValueError('`current_type` must be "straight" or "loop"')
        
        self.linear_directions = [ widgets.Image(
            value = open(f'Bfield {direction}.png', 'rb').read(), 
            format = 'png',
            width = self.width/self.n_answer_col,
            #height = 150
        ) 
                                for direction in 
                                  ['right', 'left', 'up', 'down',
                                  'out', 'in']]

        self.loop_directions = [ widgets.Image(
            value = open(f'current {direction}.png', 'rb').read(), 
            format = 'png',
            width = self.width/self.n_answer_col,
            #height = 150,
        ) 
                                for direction in 
                                ['yz-y', 'yz+y', 'xz+x', 'xz-x', 'CCW', 'CW']]

        # Dropdown menu to select what the student is looking for
        #self.unknown_choice = 'random'
        self.unknown_choices = ['random', "current", "magnetic field"]
        self.unknown_widget_dropdown = widgets.Dropdown(
            options=self.unknown_choices,
            value='random',
            description='',
            style = {'description_width': 'initial'},
            disabled=False)
        self.unknown_widget = widgets.VBox([
            widgets.HTML(
                value='Use the magnetic field right-hand-rule to find the direction of the '),
            self.unknown_widget_dropdown,
            widgets.HTML(
                r'The <span style="color:#0071bc;"><b>current is blue</b></span> and the <span style="color:#f7931e;"><b>magnetic field is orange</b></span>')])
        self.unknown_widget_dropdown.observe(self._set_unknown, 'value')
        self.correct = None
        # self.unknown_widget_dropdown.on_trait_change(self.next)
        
        # Dropdown menu to select the values from. Added a dummy
        # answer as the starting point.
        self.instruction_widget = widgets.HTML()#layout = widgets.Layout(width = f'{self.width}px'))
        self.direction_widget = widgets.GridspecLayout(3,2, grid_gap = '0px', layout = widgets.Layout(border='none', width = f'{self.width*1.1}px'))
        # widgets.Dropdown(
        #     options=[''],
        #     value=None,
        #     description='Direction:',
        #     disabled=False)
        # # callback for when a new value is selected.
        # self.direction_widget.observe(self._guess, 'value')
        
        # display of the magnetic field plot
        self.display_widget = widgets.VBox()#Label('TEST')

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
            self.instruction_widget,
            self.direction_widget, 
            self.output_widget, 
            self.next_widget])
        self._direction_events = []
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
        # local copy of the unknown choice so it can be selected from
        # random if necessary
        if self.unknown_widget_dropdown.value == 'random':
            unknown_choice = random.choice(self.unknown_choices[1:])
        else:
            unknown_choice = self.unknown_widget_dropdown.value

        # reset borders on all images
        for direction in self.loop_directions:
            direction.layout = widgets.Layout(border='none')
        for direction in self.linear_directions:
            direction.layout = widgets.Layout(border='none')

        # select the index of the problem to be presented
        problem_idx = random.choice(range(len(self.linear_directions)))
        
        # the problem and possible options depend on the type of problem
        if self.current_type == 'straight':
            if unknown_choice == 'current':
                problem = self.loop_directions[problem_idx]
                choices = self.linear_directions
            elif unknown_choice == 'magnetic field':
                problem = self.linear_directions[problem_idx]
                choices = self.loop_directions
        elif self.current_type == 'loop':
            if unknown_choice == 'current':
                problem = self.linear_directions[problem_idx]
                choices = self.loop_directions
                other = 'that creates the magentic field'
            elif unknown_choice == 'magnetic field':
                problem = self.loop_directions[problem_idx]
                choices = self.linear_directions
                other = 'created by the current loop'

        self.display_widget.children = (problem,)


        # set the choices
        self.instruction_widget.value = f'From the options below, click on the <b>direction of the {unknown_choice} {other}</b> above.'
        ichoice = 0
        for irow in range(self.direction_widget.n_rows):
            for icol in range(self.direction_widget.n_columns):
                choices[ichoice].layout = widgets.Layout(border='none')
                self.direction_widget[irow, icol] = choices[ichoice]
                ichoice += 1  
       
        for event in self._direction_events:
            del event
            
        for i, choice in enumerate(choices):
            event = ipyevents.Event(source=choice, watched_events=['click'],)
            # Note, we need to capture `choice` using `choice=choice`, otherwise it is set based on scope and the last iteration is used.
            #https://stackoverflow.com/a/7546307
            event.on_dom_event(lambda change, choice = choice: self._guess(change, widget = choice))
            self._direction_events.append(event)
    
        # self.direction_widget.options = [''] + choices
        # display the problem
        #self.display_widget.value = problem
        # set the correct answer
        self.correct = choices[problem_idx]
        self.output_widget.clear_output()
        
        
    def _guess(self, change, widget):
        '''Update the student and let them know if they are right or not.

        '''

        self.output_widget.clear_output()
        with self.output_widget:
            if widget == self.correct:
            # if change['new'] == self.correct:
                print('Correct!')
                widget.layout = widgets.Layout(border='solid green')
            # elif change['new'] == '':
            #     pass
            else:
                print('Try again.')
                widget.layout = widgets.Layout(border='solid red')

                
    def _set_unknown(self, unknown_choice):
        '''Record the user's choice of what to look for and generate a new
        problem with the appropriate options.

        '''
        self.unknown_widget_dropdown.value = unknown_choice['new']
        self.next(None)

