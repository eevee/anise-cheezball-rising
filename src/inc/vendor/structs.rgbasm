
; MIT License
;
; Copyright (c) 2018 Eldred Habert
; Originally hosted at https://github.com/ISSOtm/rgbds-structs
;
; Permission is hereby granted, free of charge, to any person obtaining a copy
; of this software and associated documentation files (the "Software"), to deal
; in the Software without restriction, including without limitation the rights
; to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
; copies of the Software, and to permit persons to whom the Software is
; furnished to do so, subject to the following conditions:
;
; The above copyright notice and this permission notice shall be included in all
; copies or substantial portions of the Software.
;
; THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
; IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
; FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
; AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
; LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
; OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
; SOFTWARE.


; struct struct_name
; Begins a struct declaration
struct: MACRO
    IF DEF(NB_FIELDS)
        FAIL "Please close struct definitions using `end_struct`"
    ENDC

STRUCT_NAME equs "\1"

NB_FIELDS = 0
    RSRESET
ENDM

; end_struct
; Ends a struct declaration
end_struct: MACRO
; Set nb of fields
STRUCT_NB_FIELDS equs "{STRUCT_NAME}_nb_fields"
STRUCT_NB_FIELDS = NB_FIELDS
    PURGE STRUCT_NB_FIELDS

; Set size of struct
STRUCT_SIZEOF equs "sizeof_{STRUCT_NAME}"
STRUCT_SIZEOF RB 0
    PURGE STRUCT_SIZEOF

    PURGE NB_FIELDS
    PURGE STRUCT_NAME
ENDM


; field_name_from_id field_id
; For internal use, please do not use externally
field_name_from_id: MACRO
FIELD_ID_STR equs "{\1}"
STRUCT_FIELD equs STRCAT("{STRUCT_NAME}_field", STRSUB("{FIELD_ID_STR}", 2, STRLEN("{FIELD_ID_STR}") - 1))
STRUCT_FIELD_NAME equs "{STRUCT_FIELD}_name"
STRUCT_FIELD_SIZE equs "{STRUCT_FIELD}_size"
ENDM


; new_field nb_elems, rs_type, field_name
; For internal use, please do not use externally
new_field: MACRO
    IF !DEF(STRUCT_NAME) || !DEF(NB_FIELDS)
        FAIL "Please start defining a struct, using `define_struct`"
    ENDC

    field_name_from_id NB_FIELDS
; Set field name
STRUCT_FIELD_NAME equs "\"\3\""
    PURGE STRUCT_FIELD_NAME

; Set field offset
STRUCT_FIELD \2 \1
; Alias this in a human-comprehensive manner
STRUCT_FIELD_NAME equs "{STRUCT_NAME}_\3"
STRUCT_FIELD_NAME = STRUCT_FIELD

; Calculate field size
CURRENT_RS RB 0
STRUCT_FIELD_SIZE = CURRENT_RS - STRUCT_FIELD

    PURGE FIELD_ID_STR
    PURGE STRUCT_FIELD
    PURGE STRUCT_FIELD_NAME
    PURGE STRUCT_FIELD_SIZE
    PURGE CURRENT_RS

NB_FIELDS = NB_FIELDS + 1
ENDM

; bytes nb_bytes, field_name
; Defines a field of N bytes
bytes: MACRO
    new_field \1, RB, \2
ENDM

; words nb_words, field_name
; Defines a field of N*2 bytes
words: MACRO
    new_field \1, RW, \2
ENDM

; longs nb_longs, field_name
; Defines a field of N*4 bytes
longs: MACRO
    new_field \1, RL, \2
ENDM


; dstruct struct_type, var_name
; Allocates space for a struct in memory (primarily RAM)
dstruct: MACRO
NB_FIELDS equs "\1_nb_fields"
    IF !DEF(NB_FIELDS)
        FAIL "Struct \1 isn't defined!"
    ENDC
STRUCT_NAME equs "\1" ; Target this struct for `field_name_from_id`

\2:: ; Declare the struct's root

FIELD_ID = 0
    REPT NB_FIELDS

        field_name_from_id FIELD_ID
FIELD_NAME equs STRCAT("\2_", STRUCT_FIELD_NAME)
FIELD_NAME::
        ds STRUCT_FIELD_SIZE

        ; Clean up vars for next iteration
        PURGE FIELD_ID_STR
        PURGE STRUCT_FIELD
        PURGE STRUCT_FIELD_NAME
        PURGE STRUCT_FIELD_SIZE
        PURGE FIELD_NAME

FIELD_ID = FIELD_ID + 1
    ENDR


    ; Define variable's properties from struct's
\2_nb_fields = NB_FIELDS
sizeof_\2 = sizeof_\1


    ; Clean up
    PURGE NB_FIELDS
    PURGE STRUCT_NAME
    PURGE FIELD_ID
ENDM
