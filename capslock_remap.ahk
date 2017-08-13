; Capslock Remapping Script 
; Danik
; danikgames.com
;
; (modified by svenlr)
; needs modification in order to be used with non-DE layouts
; this file must be saved in ANSI so ö is detected correctly
; 
; Functionality:
; - Deactivates capslock for normal (accidental) use.
; - Hold Capslock and drag anywhere in a window to move it (not just the title bar).
; - Access the following functions when pressing Capslock: 
;     Cursor keys           - I J K L 
;     Home, PgUp, PgDn, End - H U O Ö (around I J K L)
;     { [ ] } \ - can be accessed by CapsLock instead of AltGr
;  
; To use capslock as you normally would, you can press AltGr + Capslock


; This script is mostly assembled from modified versions of the following awesome scripts:
;
; # Home Row Computing by Gustavo Duarte: http://duartes.org/gustavo/blog/post/home-row-computing for 
; Changes: 
; - Does not need register remapping of AppsKey using SharpKeys.
; - Uses Vim style navigation keys (standard and works better
;   across different language layouts)
; - PgUp, PgDn, Home, End also changed to be symmetrical with Vim layout
; - Added more hotkeys for insert, undo, redo etc.
;
; # Get the Linux Alt+Window Drag Functionality in Windows: http://www.howtogeek.com/howto/windows-vista/get-the-linux-altwindow-drag-functionality-in-windows/
; Changes: The only change was using Capslock instead of Alt. This 
; also removes problems in certain applications.




#Persistent
SetCapsLockState, AlwaysOff



; Capslock + ijkl (up, left, down, right)

Capslock & i::Send {Blind}{Up DownTemp}
Capslock & i up::Send {Blind}{Up Up}

Capslock & j::Send {Blind}{Left DownTemp}
Capslock & j up::Send {Blind}{Left Up}

Capslock & k::Send {Blind}{Down DownTemp}
Capslock & k up::Send {Blind}{Down Up}

Capslock & l::Send {Blind}{Right DownTemp}
Capslock & l up::Send {Blind}{Right Up}


; Capslock + uohö (pgup, pgdown, home, end)

Capslock & o::SendInput {Blind}{PgDn Down}
Capslock & o up::SendInput {Blind}{PgDn Up}

Capslock & u::SendInput {Blind}{PgUp Down}
Capslock & u up::SendInput {Blind}{PgUp Up}

Capslock & ö::SendInput {Blind}{End Down}
Capslock & ö up::SendInput {Blind}{End Up}

Capslock & h::SendInput {Blind}{Home Down}
Capslock & h up::SendInput {Blind}{Home Up}


; CapsLock + {[]}\

CapsLock & 7::SendInput {Blind}{{ Down}
CapsLock & 7 up::SendInput {Blind}{{ Up} 

CapsLock & 8::SendInput {Blind}{[ Down}
CapsLock & 8 up::SendInput {Blind}{[ Up}

CapsLock & 9::SendInput {Blind}{] Down}
CapsLock & 9 up::SendInput {Blind}{] Up} 

CapsLock & 0::SendInput {Blind}{} Down}
CapsLock & 0 up::SendInput {Blind}{} Up} 

CapsLock & ß::SendInput {Blind}{\ Down}
CapsLock & ß up::SendInput {Blind}{\ Up} 


; Capslock + asdf (select all, cut-copy-paste)

Capslock & a::SendInput {Ctrl Down}{a Down}
Capslock & a up::SendInput {Ctrl Up}{a Up}

Capslock & s::SendInput {Ctrl Down}{x Down}
Capslock & s up::SendInput {Ctrl Up}{x Up}

Capslock & d::SendInput {Ctrl Down}{c Down}
Capslock & d up::SendInput {Ctrl Up}{c Up}

Capslock & f::SendInput {Ctrl Down}{v Down}
Capslock & f up::SendInput {Ctrl Up}{v Up}


; Capslock + wer (close tab or window, press esc)

Capslock & w::SendInput {Ctrl down}{F4}{Ctrl up}
Capslock & e::SendInput {Alt down}{F4}{Alt up}
Capslock & r::SendInput {Blind}{Esc Down}


; Capslock + nm (insert, backspace, del)

Capslock & b::SendInput {Blind}{Insert Down}
Capslock & m::SendInput {Blind}{Del Down}
Capslock & n::SendInput {Blind}{BS Down}
Capslock & BS::SendInput {Blind}{BS Down}


; Make Capslock & Enter equivalent to Control+Enter
Capslock & Enter::SendInput {Ctrl down}{Enter}{Ctrl up}


; Make Capslock & Alt Equivalent to Control+Alt
!Capslock::SendInput {Ctrl down}{Alt Down}
!Capslock up::SendInput {Ctrl up}{Alt up}


; Capslock + TAB/q (prev/next tab)

Capslock & q::SendInput {Ctrl Down}{Tab Down}
Capslock & q up::SendInput {Ctrl Up}{Tab Up}
Capslock & Tab::SendInput {Ctrl Down}{Shift Down}{Tab Down}
Capslock & Tab up::SendInput {Ctrl Up}{Shift Up}{Tab Up}

; Capslock + ,/. (undo/redo)

Capslock & ,::SendInput {Ctrl Down}{z Down}
Capslock & , up::SendInput {Ctrl Up}{z Up}
Capslock & .::SendInput {Ctrl Down}{y Down}
Capslock & . up::SendInput {Ctrl Up}{y Up}


; Make Capslock+Space -> Enter
Capslock & Space::SendInput {Enter Down}



; Make Alt Gr + Capslock work like Capslock
<^>!Capslock::
If GetKeyState("CapsLock", "T") = 1
    SetCapsLockState, AlwaysOff
Else 
    SetCapsLockState, AlwaysOn
Return





; Drag windows anywhere
;
; This script modified from the original: http://www.autohotkey.com/docs/scripts/EasyWindowDrag.htm
; by The How-To Geek
; http://www.howtogeek.com 

Capslock & LButton::
CoordMode, Mouse  ; Switch to screen/absolute coordinates.
MouseGetPos, EWD_MouseStartX, EWD_MouseStartY, EWD_MouseWin
WinGetPos, EWD_OriginalPosX, EWD_OriginalPosY,,, ahk_id %EWD_MouseWin%
WinGet, EWD_WinState, MinMax, ahk_id %EWD_MouseWin% 
if EWD_WinState = 0  ; Only if the window isn't maximized 
    SetTimer, EWD_WatchMouse, 10 ; Track the mouse as the user drags it.
return

EWD_WatchMouse:
GetKeyState, EWD_LButtonState, LButton, P
if EWD_LButtonState = U  ; Button has been released, so drag is complete.
{
    SetTimer, EWD_WatchMouse, off
    return
}
GetKeyState, EWD_EscapeState, Escape, P
if EWD_EscapeState = D  ; Escape has been pressed, so drag is cancelled.
{
    SetTimer, EWD_WatchMouse, off
    WinMove, ahk_id %EWD_MouseWin%,, %EWD_OriginalPosX%, %EWD_OriginalPosY%
    return
}
; Otherwise, reposition the window to match the change in mouse coordinates
; caused by the user having dragged the mouse:
CoordMode, Mouse
MouseGetPos, EWD_MouseX, EWD_MouseY
WinGetPos, EWD_WinX, EWD_WinY,,, ahk_id %EWD_MouseWin%
SetWinDelay, -1   ; Makes the below move faster/smoother.
WinMove, ahk_id %EWD_MouseWin%,, EWD_WinX + EWD_MouseX - EWD_MouseStartX, EWD_WinY + EWD_MouseY - EWD_MouseStartY
EWD_MouseStartX := EWD_MouseX  ; Update for the next timer-call to this subroutine.
EWD_MouseStartY := EWD_MouseY
return
