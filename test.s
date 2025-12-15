; 
; ADD INSTRUCTION TESTING 
;    
    ADD R0, R1, R7 
    ADD R3, R4, #7 ; test comment
    ADD R3, R4, #-16 ; test comment

; 
; AND INSTRUCTION TESTING 
;    
    AND R1, R2, R3 
    AND R4, R5, #7 ; test comment
    AND R6, R7, #-16 ; test comment


; 
; JMP/RET INSTRUCTION TESTING 
;    
    JMP R1 
    RET


; 
; LDR INSTRUCTION TESTING 
;    
    LDR R4, R2, #-7

; 
; NOT INSTRUCTION TESTING 
;    
    NOT R4, R2

; 
; RTI INSTRUCTION TESTING 
;    
    RTI

; 
; STR INSTRUCTION TESTING 
;    
    STR R4, R2, #-7

; 
; TRAP INSTRUCTION TESTING 
;    
    TRAP x23 ; IN