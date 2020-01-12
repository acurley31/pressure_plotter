import os
import time
import getpass
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QGroupBox,
    QFileDialog,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
)

import utils
import constants
from contour import ContourConfig, ContourPlot


# Meta data
__title__       = "Pressure Plotter"
__version__     = "0.0.1"
__author__      = "Alex Curley"
__company__     = "Stewart-Haas Racing"
__released__    = "1/13/2020"


class PressurePlotterWindow(QMainWindow):
    """Program to configure and execute the pressure plotter"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("{} v{}".format(__title__, __version__))
        self.setup_ui()
        self.setMinimumWidth(600)

        icon    = QIcon(":static/logos/shr_logo.png")
        self.setWindowIcon(icon)


    def setup_ui(self):
        """Setup the initial user interface"""

        widget  = PressurePlotterForm()
        self.setCentralWidget(widget)



class PressurePlotterForm(QWidget):
    """Pressure plotter input form widget"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._title                 = ""
        self._target_data_path      = ""#"/home/acurley/projects/shr/pressure_plotter/examples/diffuser/data/200109_121712_Run0011/D1.asc"
        self._reference_data_path   = ""#"/home/acurley/projects/shr/pressure_plotter/examples/diffuser/data/200109_115242_Run0010/D1.asc"
        self._channel_map_path      = ""#"/home/acurley/projects/shr/pressure_plotter/examples/diffuser/diffuser_channel_map_3d.csv"
        self._grid_path             = ""#"/home/acurley/projects/shr/pressure_plotter/examples/diffuser/diffuser.stl"
        self._target_label          = "Run XX"
        self._reference_label       = "Run YY"
        self._variable              = "Cp"
        self._min_absolute          = 0
        self._max_absolute          = 0.75
        self._min_delta             = -0.15
        self._max_delta             = 0.15
        self._absolute_levels       = 33
        self._delta_levels          = 17
    
        self.setup_ui()


    def setup_ui(self):
        """Set the initial user interface"""

        # Configure the main layout
        layout          = QVBoxLayout()
        group_data      = QGroupBox("Data Files")
        group_settings  = QGroupBox("Plot Settings")
        plot_button     = QPushButton("Plot")
        self.progress   = QProgressBar()
        layout.addWidget(group_data)
        layout.addWidget(group_settings)
        layout.addWidget(plot_button)
        layout.addWidget(self.progress)
        self.setLayout(layout)

        # Configure the data group box form
        grid_data  = QGridLayout(group_data)
        self._save_directory_path_edit      = QLineEdit()
        self._save_directory_button         = QPushButton("Select")
        self._target_data_path_edit         = QLineEdit()
        self._target_data_path_button       = QPushButton("Select")
        self._reference_data_path_edit      = QLineEdit()
        self._reference_data_path_button    = QPushButton("Select")
        self._channel_map_path_edit         = QLineEdit()
        self._channel_map_path_button       = QPushButton("Select")
        self._grid_path_edit                = QLineEdit()
        self._grid_path_button              = QPushButton("Select")

        # Configure the plott settings group box form
        grid_settings               = QGridLayout(group_settings)
        self._target_label_edit     = QLineEdit()
        self._reference_label_edit  = QLineEdit()
        self._variable_edit         = QLineEdit()
        self._min_absolute_edit     = QLineEdit()
        self._max_absolute_edit     = QLineEdit()
        self._min_delta_edit        = QLineEdit()
        self._max_delta_edit        = QLineEdit()

        # Set any widget settings
        self._save_directory_path_edit.setReadOnly(True)
        self._target_data_path_edit.setReadOnly(True)
        self._reference_data_path_edit.setReadOnly(True)
        self._channel_map_path_edit.setReadOnly(True)
        self._grid_path_edit.setReadOnly(True)
        self._target_label_edit.setText(self._target_label)
        self._reference_label_edit.setText(self._reference_label)
        self._variable_edit.setText(self._variable)
        self._min_absolute_edit.setText(str(self._min_absolute))
        self._max_absolute_edit.setText(str(self._max_absolute))
        self._min_delta_edit.setText(str(self._min_delta))
        self._max_delta_edit.setText(str(self._max_delta))

        self._target_data_path_edit.setText(self._target_data_path)
        self._reference_data_path_edit.setText(self._reference_data_path)
        self._channel_map_path_edit.setText(self._channel_map_path)
        self._grid_path_edit.setText(self._grid_path)
        self._target_label_edit.setText(self._target_label)
        self._reference_label_edit.setText(self._reference_label)

        # Add the widgets to the data grid
        grid_data.addWidget(QLabel("Save Directory"), 0, 0)
        grid_data.addWidget(self._save_directory_path_edit, 0, 1)
        grid_data.addWidget(self._save_directory_button, 0, 2)

        grid_data.addWidget(QLabel("Target D1"), 1, 0)
        grid_data.addWidget(self._target_data_path_edit, 1, 1)
        grid_data.addWidget(self._target_data_path_button, 1, 2)
        
        grid_data.addWidget(QLabel("Reference D1"), 2, 0)
        grid_data.addWidget(self._reference_data_path_edit, 2, 1)
        grid_data.addWidget(self._reference_data_path_button, 2, 2)

        grid_data.addWidget(QLabel("Channel Map"), 3, 0)
        grid_data.addWidget(self._channel_map_path_edit, 3, 1)
        grid_data.addWidget(self._channel_map_path_button, 3, 2)
        
        grid_data.addWidget(QLabel("Interpolation Grid"), 4, 0)
        grid_data.addWidget(self._grid_path_edit, 4, 1)
        grid_data.addWidget(self._grid_path_button, 4, 2)

        # Add widgets to the settings grid
        #grid_settings.addWidget(QLabel("Target Label"), 0, 0)
        #grid_settings.addWidget(self._target_label_edit, 0, 1)
        #grid_settings.addWidget(QLabel("Reference Label"), 1, 0)
        #grid_settings.addWidget(self._reference_label_edit, 1, 1)
        grid_settings.addWidget(QLabel("Variable Name"), 2, 0)
        grid_settings.addWidget(self._variable_edit, 2, 1)
        grid_settings.addWidget(QLabel("Absolute Scale Range"), 3, 0)
        grid_settings.addWidget(self._min_absolute_edit, 3, 1)
        grid_settings.addWidget(self._max_absolute_edit, 3, 2)
        grid_settings.addWidget(QLabel("Delta Scale Range"), 4, 0)
        grid_settings.addWidget(self._min_delta_edit, 4, 1)
        grid_settings.addWidget(self._max_delta_edit, 4, 2)

        # Connect signals and slots
        plot_button.clicked.connect(self.plot)
        self._save_directory_button.clicked.connect(self.select_save_directory)
        self._target_data_path_button.clicked.connect(self.select_target_data_path)
        self._reference_data_path_button.clicked.connect(self.select_reference_data_path)
        self._channel_map_path_button.clicked.connect(self.select_channel_map_path)
        self._grid_path_button.clicked.connect(self.select_grid_path)


    def select_save_directory(self):
        """Open a file dialog to select the save directory"""

        default = os.path.join("C:", "Users", getpass.getuser())
        dialog  = QFileDialog()
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        filename = dialog.getExistingDirectory(self, "Select Save Directory", default)

        if filename:
            self._save_directory_path  = filename
            self._save_directory_path_edit.setText(filename)
   


    def select_target_data_path(self):
        """Open a file dialog to select the target data path file"""

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, 
                        "Select Target D1 File", 
                        "", 
                        "D1 (D1.asc)",
                        options=options)

        if filename:
            self._target_data_path  = filename
            self._target_data_path_edit.setText(filename)

    
    def select_reference_data_path(self):
        """Open a file dialog to select the reference data path file"""

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, 
                        "Select Reference D1 File", 
                        "", 
                        "D1 (D1.asc)",
                        options=options)

        if filename:
            self._reference_data_path  = filename
            self._reference_data_path_edit.setText(filename)


    def select_channel_map_path(self):
        """Open a file dialog to select the channel map path file"""

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, 
                        "Select Channel Map File", 
                        "", 
                        "CSV (*.csv)",
                        options=options)

        if filename:
            self._channel_map_path  = filename
            self._channel_map_path_edit.setText(filename)

    def select_grid_path(self):
        """Open a file dialog to select the grid path file"""

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, 
                        "Select Interpolation Grid File", 
                        "", 
                        "STL (*.stl, *.STL)",
                        options=options)

        if filename:
            self._grid_path  = filename
            self._grid_path_edit.setText(filename)


    def extract_inputs(self):
        """Extract the user inputs and return the dictionary"""
        
        return {
            "target_data_path": self._target_data_path_edit.text(),
            "reference_data_path": self._reference_data_path_edit.text(),
            "channel_map_path": self._channel_map_path_edit.text(),
            "grid_path": self._grid_path_edit.text(),
            "target_label": self._target_label_edit.text(),
            "reference_label": self._reference_label_edit.text(),
            "variable": self._variable_edit.text(),
            "absolute_bounds": [float(self._min_absolute_edit.text()), float(self._max_absolute_edit.text())],
            "delta_bounds": [float(self._min_delta_edit.text()), float(self._max_delta_edit.text())],
        }


    def validate(self, inputs):
        """Validate the inputs"""
        
        for key in inputs.keys():
            value   = inputs[key]
            if not value:
                return False
            elif isinstance(value, str) and value.strip() == "":
                return False

        return True


    def plot(self):
        """Execute the plotting"""

        # Process the user inputs
        inputs  = self.extract_inputs()
        if not self.validate(inputs):
            status  = QMessageBox.critical(self, "Error: Invalid Inputs", "Please fill out all fields", QMessageBox.Ok)
            return False

        # Read any data
        target_data     = utils.read_d1(inputs.get("target_data_path"))
        reference_data  = utils.read_d1(inputs.get("reference_data_path"))
        channel_map     = utils.read_channel_map(inputs.get("channel_map_path"))
        contour         = ContourPlot(grid_path=inputs.get("grid_path"), title="")
        skip_index      = []

        # Process the channel map
        for index, row in channel_map.iterrows():
            value   = target_data.columns[target_data.columns.str.startswith(row.channel)]
            channel_map.loc[index, "channel"]  = value[0]

        # Loop through each data point
        i   = 0
        for index, item in target_data.iterrows():
            if index in skip_index or item.RRS_SPEED < 20.0:
                continue

            # Extract the matching ride height (merge if > 1 found)
            item_ref    = reference_data[
                            (reference_data["Ride-Height-Number"]==item["Ride-Height-Number"]) & \
                            (reference_data["YAW"]==item["YAW"]) & \
                            (reference_data["RRS_SPEED"]==item["RRS_SPEED"])]

            if item_ref.shape == 0:
                continue
            elif item_ref.shape[0] > 1:
                run_point   = item_ref.run_point.iloc[0]
                skip_index  += list(item_ref.index.values)
                item_ref    = item_ref.mean()
                item_ref["run_point"]   = run_point
            else:
                item_ref    = item_ref.iloc[0]


            # Calculate the values and setup the configs
            target              = channel_map.copy()
            reference           = channel_map.copy()
            delta               = channel_map.copy()
            target["value"]     = item[target.channel].values*144.0/item["DYNPR"]
            reference["value"]  = item_ref[reference.channel].values*144.0/item_ref["DYNPR"]
            delta["value"]      = target.value.values - reference.value.values


             # Setup the contour configs
            target_config   = ContourConfig(
                data=target,
                title="Target: Run {}".format(item["run_point"]),
                colormap_path=constants.DEFAULT_ABSOLUTE_COLORMAP_PATH,
                colorbar_bounds=inputs.get("absolute_bounds"),
                colorbar_levels=33,
                colorbar_label=inputs.get("variable"),
            )
    
            reference_config   = ContourConfig(
                data=reference,
                title="Reference: {}".format(item_ref["run_point"]),
                colormap_path=constants.DEFAULT_ABSOLUTE_COLORMAP_PATH,
                colorbar_bounds=inputs.get("absolute_bounds"),
                colorbar_levels=33,
                colorbar_label=inputs.get("variable"),
            )

            delta_config    = ContourConfig(
                data=delta,
                title="Target - Reference",
                colormap_path=constants.DEFAULT_DELTA_COLORMAP_PATH,
                colorbar_bounds=inputs.get("delta_bounds"),
                colorbar_levels=17,
                colorbar_label="d{}".format(inputs.get("variable")),
            )

            configs = [target_config, reference_config, delta_config]
            contour.set_configs(configs)

            target_run          = int(item["Run Number"])
            reference_run       = int(item_ref["Run Number"])
            target_run_point    = item["run_point"]
            reference_run_point = item_ref["run_point"]
            target_rh           = item["Ride-Height-Number"]
            working_directory   = self._save_directory_path_edit.text()
            save_directory      = os.path.join(working_directory, "Run_{}_vs_{}".format(target_run, reference_run))
            path                = os.path.join(save_directory, "RH-{}_Run_{}_vs_{}.png".format(target_rh, target_run_point, reference_run_point))
            
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)
            
            contour.save(path)

            percentage  = 100.0*(i + 1)/len(target_data)
            self.progress.setValue(percentage)
            i           += 1

        # Reset the progress bar
        self.progress.setValue(100)
        time.sleep(1)
        self.progress.reset()



# Execute the program
if __name__ == "__main__":
    application = QApplication([])
    window      = PressurePlotterWindow()
    window.show()
    application.exec_()
