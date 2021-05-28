#Classes for social choice test

#df headders for by round df
class Choice_Round_Indices:
    rnd = 0 #round
    b_lp = 1 #boolean lever press
    l_id = 2 #lever id (should this be 0 or 1 so we can bool them ?)
    p_lat = 3#press latency
    #any other cols ?

#df headders for daily summary df
class Choice_Daily_Summary_Indices:
    por_press = 0 #proportion of rounds lever was pressed
    ave_lat = 1 #average press latency overall
    l1_tpress = 2 #num presses for lever 1
    l1_por_t = 3 #proportion of lever 1 presses out of total opportunities
    l1_por_p = 4 #proportion of lever 1 presses out of total presses
    l1_ave_lat = 5 #average latency of only lever 1 presses
    l2_tpress = 6 #num presses for lever 2
    l2_por_t = 7 #proportion of lever 2 presses out of total opportunities
    l2_por_p = 8 #proportion of lever 2 presses out of total presses
    l2_ave_lat = 9 #average latency of only lever 2 presses
    #should we have a vole and date cols as well? 

#class for unique event strings
class Operant_event_strings:
    pulse_sync_line_01 = ' pulse sync line|0.1'
    new_round = ' Starting new round'
    round_start_tone = ' round_start_tone tone start 3000:hz 1:seconds'
    round_end_tone = ' round_start_tone tone complete 3000:hz 1:seconds' 
    lever_out = ' Levers out'
    lever_retracted = ' Levers retracted'
    door1_leverpress_prod = ' door_1 lever pressed productive'
    door2_leverpress_prod = ' door_2 lever pressed productive'
    pulse_sync_line_025 = ' pulse sync line|0.025' 
    door_open_tone_start = ' door_open_tone tone start 10000:hz 1:seconds'
    door_open_tone_end = ' door_open_tone tone complete 10000:hz 1:seconds'
    move_animal_time_start = ' start of move animal time' 
    door_close_tone_start = ' door_close_tone tone start 7000:hz 1:seconds'
    door_close_tone_end = ' door_close_tone tone complete 7000:hz 1:seconds'
    
    door1_open_start = ' door_1 open begin'
    door1_open_end = ' door_1 open finish' 
    door1_open_failure = ' door_1 open failure'
    door1_close = ' door_1 close begin'
    
    door2_open_start = ' door_2 open begin'
    door2_open_end = ' door_2 open finish' 
    door2_open_failure = ' door_2 open failure'
    door2_close = ' door_2 close begin'

    food_leverpress_prod = ' food lever pressed productive'
    disp = ' Pellet dispensed'
    retr = ' pellet retrieved'

    beam_break_1 = ' beam_break_1_crossed'
    beam_break_2 = ' beam_break_2_crossed'

    first_beam_break_1 = ' first_beam_break_1_crossed'
    first_beam_break_2 = ' first_beam_break_2_crossed'
    
    #I kept the space for now
    #also may need to add others, I was working from a door shape file
    #maybe don't need all of these either but just to be safe