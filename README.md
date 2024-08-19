# Volume Control App

## Description

**Volume Control App** is an easy-to-use application for managing application volume in Windows. It allows you to easily adjust the volume level for a selected application and switch between two preset volume levels using a convenient graphical interface and hotkeys.

## Features

- **Application Selection**: Choose an application from the list of running processes on your computer. The app displays a list of all active processes, allowing you to select the desired application to adjust its volume.
- **Volume Control**:
  - **Slider for Setting the First Volume Level**: Set the minimum volume level that will be applied to the selected application when activated.
  - **Slider for Setting the Second Volume Level**: Set the maximum volume level that will be applied to the selected application when toggling.
- **Current Volume Display**: The app displays the current volume level for the selected application. This information is updated in real-time as the volume changes.
- **Hotkeys**:
  - **Ctrl + F2**: Toggle between the two preset volume levels. The first press sets the first volume level, and a subsequent press sets the second volume level. This is default hotkey, you can change it. Changed hotkey saved in `hotkey.txt` file
- **Automatic Application Saving**: The selected application is automatically saved to a file `process.txt` next to the executable file. On the next launch, the application automatically loads the last selected process if it is active.

## Running Instructions

1. **Download** the latest version of Volume Control App from the repository.
2. **Run** the `AppVolumeControl.exe` file to use the application.

## System Requirements

- **Operating System**: Windows 10 or newer

## License

Volume Control App is distributed under the [MIT License](https://opensource.org/licenses/MIT).
