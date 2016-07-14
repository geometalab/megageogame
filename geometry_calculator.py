'''
Created on 23.05.2014

@author: Ausleihe
'''
from math import sin, cos, sqrt, atan2, radians, atan, tan, fabs


class GeometryHandler(object):
    '''
    This class handles geometrical calculations
    '''


    def __init__(self):
        self.ambigous_constant_1 = 6378137
        self.ambigous_constant_2 = 6356752.314245
        self.floor_value_constant = 1 / 298.257223563

    def get_distance(self, point1, point2):
        '''
        Calculates the distance between two points after formula from
        http://www.movable-type.co.uk/scripts/latlong-vincenty.html
        Didn't spend much time understanding the math, code is rittled
        with magic numbers
        '''
        latitude1 = point1[0]
        longitude1 = point1[1]
        latitude2 = point2[0]
        longitude2 = point2[1]
        longitude_distance = radians(longitude2 - longitude1)
        angle1 = atan((1 - self.floor_value_constant) * tan(radians(latitude1)))
        angle2 = atan((1 - self.floor_value_constant) * tan(radians(latitude2)))
        sin_of_angle_1 = sin(angle1)
        cos_of_angle_1 = cos(angle1)
        sin_of_angle_2 = sin(angle2)
        cos_of_angle_2 = cos(angle2)
        epsilon_1 = longitude_distance
        epsilon_2 = 500
        iter_limit = 100
        while fabs(epsilon_1 - epsilon_2) > 0.000001 and iter_limit > 0:
            sin_of_epsilon_1 = sin(epsilon_1)
            cos_of_epsilon_1 = cos(epsilon_1)
            sin_of_sigma = sqrt(
                (cos_of_angle_2 * sin_of_epsilon_1)
                * (cos_of_angle_2 * sin_of_epsilon_1)
                + (
                    cos_of_angle_1
                    * sin_of_angle_2
                    - sin_of_angle_1
                    * cos_of_angle_2
                    * cos_of_epsilon_1
                    )
                * cos_of_angle_1
                * sin_of_angle_2
                - sin_of_angle_1
                * cos_of_angle_2
                * cos_of_epsilon_1
                )
            if sin_of_sigma == 0:
                return 0
            cos_of_sigma = (
                sin_of_angle_1
                * sin_of_angle_2
                + cos_of_angle_1
                * cos_of_angle_2
                * cos_of_epsilon_1
                )
            sigma = atan2(sin_of_sigma, cos_of_sigma)
            sin_of_alpha = (
                cos_of_angle_1
                * cos_of_angle_2
                * sin_of_epsilon_1
                / sin_of_sigma
                )
            cos_of_alpha = 1 - sin_of_alpha * sin_of_alpha
            cos_of_sigma_2 = (
                cos_of_sigma
                - 2
                * sin_of_angle_1
                * sin_of_angle_2
                / cos_of_alpha
                )
            if cos_of_sigma_2 is None:
                cos_of_sigma_2 = 0
            ambigous_angle = (
                self.floor_value_constant
                / 16
                * cos_of_alpha
                * (4 + self.floor_value_constant * (4 - 3 * cos_of_alpha)))
            epsilon_2 = epsilon_1
            epsilon_1 = (
                longitude_distance
                + (1 - ambigous_angle)
                * self.floor_value_constant
                * sin_of_alpha
                * (
                    sigma
                    + ambigous_angle
                    * sin_of_sigma
                    * (
                        cos_of_sigma_2
                        + ambigous_angle
                        * cos_of_sigma
                        * (-1 + 2 * cos_of_sigma_2 * cos_of_sigma_2)
                        )
                    )
                )
            iter_limit -= 1
        ambigous_constant_from_angles = (
            cos_of_alpha
            * (
                self.ambigous_constant_1
                * self.ambigous_constant_1
                - self.ambigous_constant_2
                * self.ambigous_constant_2
                )
            / (self.ambigous_constant_2 * self.ambigous_constant_2)
            )
        ambigous_number = (
            1
            + ambigous_constant_from_angles
            / 16384
            * (
                4096
                + ambigous_constant_from_angles
                * (
                    -768
                    + ambigous_constant_from_angles
                    * (320 - 175 * ambigous_constant_from_angles)
                    )
                )
            )
        ambigous_number_2 = (
            ambigous_constant_from_angles
            / 1024
            * (
                256
                + ambigous_constant_from_angles
                * (
                    -128
                    + ambigous_constant_from_angles
                    * (74 - 47 * ambigous_constant_from_angles)
                    )
                )
            )
        delta_sigma = (
            ambigous_number_2
            * sin_of_sigma
            * (
                cos_of_sigma_2
                + ambigous_number_2
                / 4
                * (
                    cos_of_sigma
                    * (-1 + 2 * cos_of_sigma_2 * cos_of_sigma_2)
                    - ambigous_number_2
                    / 6
                    * cos_of_sigma_2
                    * (-3 + 4 * sin_of_sigma * sin_of_sigma)
                    * (-3 + 4 * cos_of_sigma_2 * cos_of_sigma_2)
                    )
                )
            )
        distance = (
            self.ambigous_constant_2
            * ambigous_number
            * (sigma - delta_sigma)
            )
        return distance
