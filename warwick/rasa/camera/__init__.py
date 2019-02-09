#
# This file is part of rasa-camd
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

"""camd common code"""

from .constants import CommandStatus, CameraStatus
from .validation import configure_validation_schema
from .gpstimer import GPSTimer, GPSFixType, GPSLocalCheckStatus
