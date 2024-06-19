# This file is used to calculate the aircraft geometry based on the input parameters
import numpy as np
import json
np.set_printoptions(precision=8)


class aircraft_geometry:
    """This class is used to calculate the aircraft geometry based on the input parameters"""
    def __init__(self, input_data):
        self.input_data = input_data
        self.load_json()
        print("")
        print("Lifting Surface Name:", self.lifting_surface_name)
        if self.swept:
            self.calculate_geometry()
            if self.has_control_surface:
                self.control_surface_geometry()
            else:
                print("")
        else:
            self.unswept_geometry()
            if self.has_control_surface:
                self.control_surface_geometry()
            else:
                print("")
        print("")

    def load_json(self):
        """
        This function pulls in all the input values from the json.

        It reads the input values from a JSON file and assigns them to the corresponding class attributes.

        Args:
            None

        Returns:
            None
        """    
        with open(self.input_data, 'r') as json_handle:
            input_vals = json.load(json_handle)

            # lifting surface json values
            self.lifting_surface_name = input_vals["lifting_surface"]["name[str]"]
            self.length_from_nose_to_leading_edge_at_root = inches_to_feet(input_vals["lifting_surface"]["length_from_nose_to_leading_edge_at_root[in]"])
            self.parallel_length = inches_to_feet(input_vals["lifting_surface"]["length_parallel_to_unswept_segment[in]"])
            self.perpendicular_length = inches_to_feet(input_vals["lifting_surface"]["length_perpendicular_to_unswept_segment[in]"])
            self.root_chord = inches_to_feet(input_vals["lifting_surface"]["root_chord[in]"])
            self.tip_chord = inches_to_feet(input_vals["lifting_surface"]["tip_chord[in]"])
            self.semispan = inches_to_feet(input_vals["lifting_surface"]["semispan[in]"])
            self.b = 2 * self.semispan
            self.thickness = inches_to_feet(input_vals["lifting_surface"]["thickness[in]"])
            self.swept = input_vals["lifting_surface"]["swept[bool]"]

            # control surface json values
            self.control_surface_name = input_vals["control_surface"]["name[str]"]
            self.has_control_surface = input_vals["control_surface"]["has_control_surface[bool]"]
            self.spanwise_distances_from_root = input_vals["control_surface"]["spanwise_distance_from_root[in]"]
            self.spanwise_distances_from_root[0] = inches_to_feet(self.spanwise_distances_from_root[0])
            self.spanwise_distances_from_root[1] = inches_to_feet(self.spanwise_distances_from_root[1])
            self.control_surface_chords = input_vals["control_surface"]["chord[in]"]
            self.control_surface_chords[0] = inches_to_feet(self.control_surface_chords[0])
            self.control_surface_chords[1] = inches_to_feet(self.control_surface_chords[1])
            self.control_surface_thickness = input_vals["control_surface"]["thickness[in]"]
            self.control_surface_thickness[0] = inches_to_feet(self.control_surface_thickness[0])
            self.control_surface_thickness[1] = inches_to_feet(self.control_surface_thickness[1])

    def calculate_x_offset_from_nose(self):
        """
        Calculates the x offset from the nose of the aircraft geometry.

        The x offset from the nose is calculated as the length from the nose to the leading edge at the root
        minus the parallel length of the aircraft geometry.

        Returns:
            None

        """
        self.x_offset_from_nose = -self.length_from_nose_to_leading_edge_at_root - (self.root_chord*0.25)
    
    def calculate_le_sweep_angle(self):
        """
        Calculates the leading edge sweep angle of the aircraft geometry.

        The leading edge sweep angle is calculated using the perpendicular length and parallel length
        of the aircraft geometry. Specifically, the leading edge sweep angle is calculated as the arc tangent 
        of the perpendicular length divided by the parallel length.

        Returns:
            None

        """
        self.le_sweep_angle = np.arctan2(self.perpendicular_length, self.parallel_length) # in radians
        
    def calculate_taper_ratio(self):
        """
        Calculates the taper ratio of the aircraft geometry.

        The taper ratio is calculated as the tip chord divided by the root chord.

        Returns:
            None

        """
        self.taper_ratio = self.tip_chord / self.root_chord
        self.control_surface_taper_ratio = self.control_surface_chords[1] / self.control_surface_chords[0]

    def calculate_quarter_chord_sweep_angle(self):
        """
        Calculates the quarter chord sweep angle of the aircraft geometry.

        The quarter chord sweep angle is calculated using the leading edge sweep angle and the taper ratio.
        Specifically, the quarter chord sweep angle is calculated as the arc tangent of the taper ratio times the tangent of the leading edge sweep angle.

        Returns:
            None

        """
        self.quarter_chord_sweep_angle = np.arctan(np.tan(self.le_sweep_angle)+2*(0.25/self.b)*self.root_chord*(self.taper_ratio-1))

    def calculate_thicknesses(self):
        """
        Calculates the thicknesses of the aircraft geometry.

        The thicknesses are calculated using the thickness and the root chord of the aircraft geometry.
        Specifically, the thicknesses are calculated as the thickness divided by the root and tip chords.

        Returns:
            None

        """
        if self.root_chord == 0:
            self.thickness_root = "N/A"
        else:
            self.thickness_root = self.thickness / self.root_chord
        if self.tip_chord == 0:
            self.thickness_tip = "N/A"
        else:
            self.thickness_tip = self.thickness / self.tip_chord
        self.thickness_control_surface_root = self.control_surface_thickness[0] / self.control_surface_chords[0]
        self.thickness_control_surface_tip = self.control_surface_thickness[1] / self.control_surface_chords[1]

    def calculate_control_surface_spanwise_locations(self):
        """
        Calculates the spanwise locations of the control surfaces.

        The spanwise locations of the control surfaces are calculated using the spanwise distances from the root
        of the aircraft geometry and the semispan. Specifically, the spanwise locations of the control surfaces are
        calculated as the spanwise distances from the root divided by the semispan.

        Returns:
            None

        """
        self.control_surface_spanwise_location_root = self.spanwise_distances_from_root[0] / self.semispan
        self.control_surface_spanwise_location_tip = self.spanwise_distances_from_root[1] / self.semispan
    
    def calculate_control_surface_chord_fraction(self):
        """
        Calculates the control surface chord fraction.

        The control surface chord fraction is calculated using the control surface chord and the root chord.
        Specifically, the control surface chord fraction is calculated as the control surface chord divided by the root chord.

        Returns:
            None

        """
        self.control_surface_chord_fraction_root = self.control_surface_chords[0] / self.root_chord
        self.control_surface_chord_fraction_tip = self.control_surface_chords[1] / self.tip_chord

    def calculate_geometry(self):
        """
        Calculates the aircraft geometry.

        This function calculates the aircraft geometry by calling the functions that calculate the leading edge sweep angle,
        taper ratio, and quarter chord sweep angle.

        Returns:
            None

        """
        self.calculate_le_sweep_angle()
        self.calculate_taper_ratio()
        self.calculate_thicknesses()
        self.calculate_x_offset_from_nose()
        self.calculate_quarter_chord_sweep_angle()

        print("Swept Geometric Parameters")
        print("x offset from nose[ft]: ", self.x_offset_from_nose)
        print("Chord at root[ft]: ", self.root_chord)
        print("Chord at tip[ft]: ", self.tip_chord)
        print("Leading edge sweep angle[deg]: ", np.degrees(self.le_sweep_angle))
        print("Taper ratio: ", self.taper_ratio)
        print("Quarter chord sweep angle[deg]: ", np.degrees(self.quarter_chord_sweep_angle))
        print("Thickness divided by root chord: ", self.thickness_root)
        print("Thickness divided by tip chord: ", self.thickness_tip)
        print("semispan[ft]: ", self.semispan)
        print("\n")

    def unswept_geometry(self):
        """
        Calculates and prints unswept geometric parameters of the aircraft.

        This method calculates the taper ratio, thickness divided by root chord, and thickness divided by tip chord
        for the unswept geometry of the aircraft. It then prints these parameters to the console.

        Parameters:
            None

        Returns:
            None
        """
        self.calculate_taper_ratio()
        self.calculate_thicknesses()
        self.calculate_x_offset_from_nose()
        print("Unswept Geometric Parameters")
        print("x offset from nose[ft]: ", self.x_offset_from_nose)
        print("Chord at root[ft]: ", self.root_chord)
        print("Chord at tip[ft]: ", self.tip_chord)
        print("Taper ratio: ", self.taper_ratio)
        print("Thickness divided by root chord: ", self.thickness_root)
        print("Thickness divided by tip chord: ", self.thickness_tip)
        print("semispan[ft]: ", self.semispan)
        print("\n")

    def control_surface_geometry(self):
        """
        Calculates and prints the geometric parameters of the control surface.

        This method calculates the taper ratio, thickness divided by root chord, and thickness divided by tip chord
        for the control surface of the aircraft. It then prints these parameters to the console.

        Parameters:
            None

        Returns:
            None
        """
        print("Control Surface Name:", self.control_surface_name)
        self.calculate_control_surface_spanwise_locations()
        self.calculate_control_surface_chord_fraction()
        print("Control Surface Chord Fraction Root: ", self.control_surface_chord_fraction_root)
        print("Control Surface Chord Fraction Tip: ", self.control_surface_chord_fraction_tip)
        print("Control Surface Taper Ratio: ", self.control_surface_taper_ratio)
        print("Control Surface Thickness divided by Root Chord: ", self.thickness_control_surface_root)
        print("Control Surface Thickness divided by Tip Chord: ", self.thickness_control_surface_tip)
        print("Control Surface Spanwise Location Root: ", self.control_surface_spanwise_location_root)
        print("Control Surface Spanwise Location Tip: ", self.control_surface_spanwise_location_tip)

def inches_to_feet(inches):
    """
    This function converts inches to feet.

    Args:
        inches (float): The length in inches to be converted to feet.

    Returns:
        float: The length in feet.
    """
    return inches / 12.0

if __name__ == "__main__":
    # input_data = json.load(open("calculate_aircraft_geometry.json"))
    input_data = "calculate_aircraft_geometry.json"
    aircraft_geometry(input_data)