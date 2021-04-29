; Autohotkey script for saving scenarios.
; Right now it doesn't accept input. Edit the variables for the scenario name,
; the start index (inclusive), and the number of scenarios.
; And also edit the path to `copyscn.py`.

; Be sure to set up the scenario editor before pressing Windows+z to run.
; The script should be run starting on the "Map" tab of the scenario editor.
; The scenario and output directories must not contain any file with a name
; that would be overwritten by saving
; (the script does not detect the "are you sure" popup).

; The script must be run individually for each scenario (after setting up the)
; editor. It does not currently cycle through different random map scripts.

; The script also requires Python to be installed. It calls a Python script
; to move scenarios out of DE's scenario directory. If we just be the scenarios
; in that directory, then DE would take longer and longer to process them
; while opening the "Save As" menu.

; The name of the scenario.
; The output file is named: scnname . "-" . index . ".aoe2scenario"
scnname := "twogroups"

; The first index to use in the name of a saved file.
startindex := 0

; The number of scenario files to create.
numscn := 1000

; An x screen coordinate inside of the Generate Map button.
genmapx := 380

; A y screen coordinate inside of the Generate Map button.
genmapy := 1360

GenScn(name, start, n, genmapx, genmapy) {
    CoordMode, Mouse, Screen
    endindex := start + n
    k := start
    Sleep 1000
    while k != endindex {
        ; Clicks "Generate Map".
        MouseMove, genmapx, genmapy
        Sleep 25
        MouseClick, Left
        Sleep 1500

        ; Presses Ctrl+Shift+S to Save As.
        Send ^+s
        Sleep 250

        ; Selects the entire name.
        Send ^a
        Sleep 50

        ; Inputs the new name.
        Send % name . "-" . k
        Sleep 250

        ; Presses Enter to save the scenario.
        Send {Enter}
        Sleep 750

        ; Moves the Scenario file to an output directory.
        ; Probably could use a relative path instead...
        Run python "ABSOLUTE_PATH_TO\copyscn.py"
        Sleep 100

        k := k + 1
    }
    MsgBox % "Finished processing scenario " . name . "."
    return
}

PrintMouse() {
    mousex := 0
    mousey := 0
    CoordMode, Mouse, Screen
    MouseGetPos, mousex, mousey
    MsgBox % "(" . mousex . ", " . mousey . ")"
    return
}

#z::ExitApp

^t::
GenScn(scnname, startindex, numscn, genmapx, genmapy)
return
