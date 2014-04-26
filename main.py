
from kivy.app import App

from kivy.uix.widget import Widget
from kivy.uix.effectwidget import EffectWidget, FXAAEffect
from kivy.core.window import Window
from kivy.clock import Clock

import kivent
from kivent import GameSystem

from random import randint
from math import radians
from functools import partial

class BoundarySystem(GameSystem):

    def generate_boundary(self, pos, size):
        gameworld = self.gameworld
        shape_dict = {'width': size[0],
                      'height': size[1],
                      'mass': 0}
        col_shape_dict = {'shape_type': 'box',
                          'elasticity': 0.0,
                          'collision_type': 2,
                          'shape_info': shape_dict,
                          'friction': 0.0}
        physics_component_dict = {'main_shape': 'box',
                                  'velocity': (0, 0),
                                  'position': pos,
                                  'angle': 0,
                                  'angular_velocity': 0,
                                  'mass': 0,
                                  'vel_limit': 0,
                                  'ang_vel_limit': 0,
                                  'col_shapes': [col_shape_dict]}
        boundary_system = {}
        create_component_dict = {
            'position': pos,
            'rotate': 0.,
            'color': (1.0, 0.0, 0.0, 0.75),
            'physics': physics_component_dict,
            'boundary': boundary_system,
            'debug_renderer': {'size': size}}
        component_order = ['position', 'rotate', 'color',
                           'physics', 'boundary', 'debug_renderer']
        self.gameworld.init_entity(create_component_dict, component_order)

    def clear(self):
        gameworld = self.gameworld
        remove = gameworld.timed_remove_entity
        for entity_id in self.entity_ids:
            Clock.schedule_once(partial(remove, entity_id))


class BubblesGame(EffectWidget):
    def __init__(self, **kwargs):
        super(BubblesGame, self).__init__(**kwargs)
        self.effects = [FXAAEffect()]
        Clock.schedule_once(self.init_game)

    def init_game(self, dt):
        self.setup_map()
        self.setup_states()
        self.set_state()
        self.create_bubbles()
        Clock.schedule_interval(self.update, 0)

    def update(self, dt):
        self.gameworld.update(dt)

    def setup_map(self):
        gameworld = self.gameworld
        gameworld.currentmap = gameworld.systems['map']

    def setup_states(self):
        self.gameworld.add_state(state_name='main',
                                 systems_added=['debug_renderer',
                                                'physics_renderer'],
                                 systems_removed=[],
                                 systems_paused=[],
                                 systems_unpaused=['debug_renderer',
                                                   'physics_renderer'],
                                 screenmanager_screen='main')

    def set_state(self):
        self.gameworld.state = 'main'

    def create_bubbles(self):
        size = Window.size
        for x in range(50):
            pos = (randint(0, size[0]), randint(0, size[1]))
            self.create_bubble(pos)

    def on_touch_down(self, touch):
        super(BubblesGame, self).on_touch_down(touch)
        self.on_touch_move(touch)

    def on_touch_move(self, touch):
        super(BubblesGame, self).on_touch_move(touch)
        bs = self.gameworld.systems['boundary']
        bs.clear()
        bs.generate_boundary((0, 0), touch.pos)

    def create_bubble(self, pos):
        print 'creating bubble'
        x_vel = randint(-100, 100)
        y_vel = randint(-100, 100)

        angle = radians(randint(-360, 360))
        angular_velocity = 0.

        shape_dict = {'inner_radius': 0,
                      'outer_radius': 32,
                      'mass': 50,
                      'offset': (0, 0)}
        col_shape = {'shape_type': 'circle',
                     'elasticity': .5,
                     'collision_type': 1,
                     'shape_info': shape_dict,
                     'friction': 1.0}
        col_shapes = [col_shape]
        physics_component = {'main_shape': 'circle',
                             'velocity': (x_vel, y_vel),
                             'position': pos,
                             'angle': angle,
                             'angular_velocity': angular_velocity,
                             'vel_limit': 250,
                             'ang_vel_limit': radians(200),
                             'mass': 50,
                             'col_shapes': col_shapes}
        create_component_dict = {'physics': physics_component,
                                 'physics_renderer': {'texture': 'black_stone',
                                                      'size': (64, 64)},
                                 'position': pos,
                                 'rotate': 0}
        component_order = ['position', 'rotate', 'physics', 'physics_renderer']
        result = self.gameworld.init_entity(create_component_dict,
                                            component_order)
        print 'result is', result
        return result


class BubblesApp(App):
    def build(self):
        Window.clearcolor = (0.5, 0.5, 0.5, 1)


if __name__ == "__main__":
    BubblesApp().run()
