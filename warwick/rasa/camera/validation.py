#!/usr/bin/env python3
#
# This file is part of rasa-camd.
#
# rasa-camd is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rasa-camd is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rasa-camd.  If not, see <http://www.gnu.org/licenses/>.

"""Validation schema used by opsd to verify observation schedule blocks"""

def configure_validation_schema(camera):
    """Returns a jsonschema object for validating the
       params object passed to the configure method

       camera takes the camera id to parse
    """

    return {
        'type': 'object',
        'additionalProperties': False,
        'required': ['exposure'],
        'properties': {
            'temperature': {
                'type': 'number',
                'minimum': -80,
                'maximum': 0,
            },
            'cooler': {
                'type': 'boolean'
            },
            'shutter': {
                'type': 'boolean'
            },
            'exposure': {
                'type': 'number',
                'minimum': 0
            },
            'delay': {
                'type': 'number',
                'minimum': 0
            }
        }
    }
