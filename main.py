
from kivy.app import App

from kivy.uix.widget import Widget
from kivy.uix.effectwidget import EffectWidget, FXAAEffect
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.properties import ListProperty, DictProperty, NumericProperty

import kivent
from kivent import GameSystem

from random import randint
from math import radians, sqrt
from functools import partial

import ipdb

class BubbleSystem(GameSystem):

    def create_bubble(self, pos):
        x_vel = randint(-100, 100)
        y_vel = randint(-100, 100)

        angle = radians(randint(-360, 360))
        angular_velocity = 0.

        shape_dict = {'inner_radius': 0,
                      'outer_radius': 32,
                      'mass': 50,
                      'offset': (0, 0)}
        col_shape = {'shape_type': 'circle',
                     'elasticity': 1.,
                     'collision_type': 1,
                     'shape_info': shape_dict,
                     'friction': 10.0}
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
                                 'bubble': {},
                                 'rotate': 0}
        component_order = ['position', 'rotate', 'physics', 'bubble', 'physics_renderer']
        result = self.gameworld.init_entity(create_component_dict,
                                            component_order)
        return result


class BoundarySystem(GameSystem):

    def generate_boundaries(self, pos, size, length_frac=0.5):
        '''Generates boundaries around the outside of the given
        rectangle.'''
        pos = Vector(pos)
        size = Vector(size)
        bottom_pos = (pos[0] + 0.5*size[0],
                      pos[1] - 0.5*length_frac*size[1] + 10)
        bottom_size = (size[0]*2, length_frac*size[1])
        top_pos = (pos[0] + 0.5*size[0],
                   pos[1] + (1+0.5*length_frac)*size[1] - 10)
        top_size = (size[0]*2, length_frac*size[1])
        left_pos = (pos[0] - 0.5*length_frac*size[0] + 10,
                    pos[1] + 0.5*size[1])
        left_size = (size[0]*length_frac, size[1]*2)
        right_pos = (pos[0] + (1 + 0.5*length_frac)*size[0] - 10,
                     pos[1] + 0.5*size[1])
        right_size = (size[0]*length_frac, size[1]*2)

        self.generate_boundary(bottom_pos, bottom_size)
        self.generate_boundary(top_pos, top_size)
        self.generate_boundary(left_pos, left_size)
        self.generate_boundary(right_pos, right_size)
        

    def generate_boundary(self, pos, size): 
        pos = tuple(pos)
        size = tuple(size)
        gameworld = self.gameworld
        shape_dict = {'width': size[0],
                      'height': size[1],
                      'mass': 0}
        col_shape_dict = {'shape_type': 'box',
                          'elasticity': 1.,
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
        remove = gameworld.remove_entity
        for entity_id in self.entity_ids:
            remove(entity_id)
            # Clock.schedule_once(partial(remove, entity_id), 0)


class BubblesGame(EffectWidget):

    boundary_pos = ListProperty([0, 0])
    boundary_size = ListProperty([200, 200])

    touches = DictProperty([])

    elasticity = NumericProperty()
    friction = NumericProperty()
    radius = NumericProperty()
    damping = NumericProperty()
    
    def __init__(self, **kwargs):
        super(BubblesGame, self).__init__(**kwargs)
        self.effects = [FXAAEffect()]
        Clock.schedule_once(self.init_game)


    def init_game(self, dt):
        self.setup_map()
        self.setup_states()
        self.set_state()
        Clock.schedule_interval(self.update, 0)

        self.bind(boundary_pos=self.redraw_boundaries,
                  boundary_size=self.redraw_boundaries)

        self.bind(pos=self.setter('boundary_pos'),
                  size=self.setter('boundary_size'))

        self.boundary_pos = self.pos
        self.boundary_size = self.size

        self.create_bubbles()

    def update(self, dt):
        self.move_entities_with_touch()
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
        bubble_system = self.gameworld.systems['bubble']
        for x in range(10):
            pos = (randint(100, 200), randint(100, 200))
            bubble_system.create_bubble(pos)

    def on_damping(self, *args):
        damping = self.damping
        try:
            self.gameworld.systems['physics'].space.damping = damping
        except KeyError:
            pass

    def on_elasticity(self, *args):
        elasticity = self.elasticity
        self.set_shape_attrs('elasticity', elasticity)

    def on_friction(self, *args):
        friction = self.friction
        self.set_shape_attrs('friction', friction)

    def on_radius(self, *args):
        radius = self.radius
        gw = self.gameworld
        try:
            bubble_system = gw.systems['bubble']
            entity_ids = bubble_system.entity_ids
            for eid in entity_ids:
                entity = gw.entities[eid]
                entity.physics.shapes[0].unsafe_set_radius(radius)
        except KeyError:
            pass

    def set_shape_attrs(self, attr_name, value):
        gw = self.gameworld
        try:
            bubble_system = gw.systems['bubble']
            entity_ids = bubble_system.entity_ids
            for eid in entity_ids:
                entity = gw.entities[eid]
                setattr(entity.physics.shapes[0], attr_name,
                        value)
                gw.systems['physics'].space.reindex_shape(
                    entity.physics.shapes[0])

        except KeyError:
            pass
        
        

    def on_touch_down(self, touch):
        super(BubblesGame, self).on_touch_down(touch)

        # Grab bubble
        radius = 50
        gw = self.gameworld
        bubble_system = gw.systems['bubble']
        entity_ids = bubble_system.entity_ids
        tpos = Vector(touch.pos)
        match = None
        for eid in entity_ids:
            entity = gw.entities[eid]
            dr = (Vector([entity.position.x, entity.position.y]) -
                  Vector(touch.pos))
            dist = sqrt(dr[0]**2 + dr[1]**2)
            if dist < radius:
                match = entity
                break
        if match is None:
            return

        #ipdb.set_trace()

        touch.ud['entity'] = (entity, dr)
        self.touches[touch] = [touch, entity, dr, (0., 0.)]
        self.move_entities_with_touch()


    def on_touch_up(self, touch):
        if touch in self.touches:
            touch, entity, dr, force = self.touches.pop(touch)
            entity.physics.body.apply_force((-1*force[0], -1*force[1]))


    def move_entities_with_touch(self, *args):
        for touch, values in self.touches.items():
            touch, entity, dr, force = values
            entity.physics.body.apply_force((-1*force[0], -1*force[1]))
            dr = (Vector([entity.position.x, entity.position.y]) -
                  Vector(touch.pos))
            dist = sqrt(dr[0]**2 + dr[1]**2)
            new_force = tuple([-100*dr[0], -100*dr[1]])
            values[3] = new_force
            entity.physics.body.apply_force(new_force)

    def redraw_boundaries(self, *args):
        bs = self.gameworld.systems['boundary']
        bs.clear()
        bs.generate_boundaries(self.boundary_pos, self.boundary_size)

class Interface(BoxLayout):
    pass

class BubblesApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)



if __name__ == "__main__":
    BubblesApp().run()
