import turtle
import pygame
import time
import os
import math

pygame.mixer.init()

wn_height = 1600
wn_widht = 1600

player_recuo = 200

player_height = 130
player_width = 10

ball_size = 30

player1_ac = 3
player2_ac = 3
score_a = 0
score_b = 0

wn = turtle.Screen()
wn.title = (" pong !")
wn.bgcolor("black")
wn.setup(width=wn_widht, height=wn_height)
wn.tracer(0)              

player1 = turtle.Turtle()
player1.speed(0)
player1.shape("square")
player1.shapesize(stretch_len=player_width / 20 , stretch_wid=player_height / 20)
player1.color("white")
player1.penup()
player1.goto(-wn_widht/2 +player_recuo, 0)
player1.a = player1_ac
player1.d = player1_ac

# Variáveis para o sistema de dash
player1.dash_active = False
player1.dash_velocity = 0
player1.dash_direction = 0
player1.dash_decay = 0.79
player1.dash_initial_speed = 45
player1.dash_cooldown = 0
player1.dash_cooldown_time = 1  # frames de cooldown

# Variáveis para o sistema de impulso (charge)
player1.charge_active = False
player1.charge_level = 0
player1.max_charge = 50
player1.charge_rate = 1
player1.charge_decay_rate = 10 # Taxa de perda de carga quando não está carregando

player2 = turtle.Turtle()
player2.speed(0)
player2.shape("square")
player2.shapesize(stretch_len=player_width / 20, stretch_wid= player_height / 20)
player2.color("white")
player2.penup()
player2.goto(wn_widht/2 -player_recuo, 0)

# Variáveis para a IA do Player 2
player2.current_speed = 0
player2.acceleration = -1.1 # Aceleração inicial da IA
player2.max_speed = 5     # Velocidade máxima da IA
player2.min_speed = 1      # Velocidade mínima da IA

# Variáveis para o sistema de dash da IA
player2.dash_active = False
player2.dash_velocity = 0
player2.dash_direction = 0
player2.dash_decay = 0.79
player2.dash_initial_speed = 45  # Ligeiramente menor que o jogador 1
player2.dash_cooldown = 0
player2.dash_cooldown_time = 17  # Cooldown maior que o jogador 1 para balanceamento
player2.dash_trigger_distance = 105  # Distância da bola para ativar dash



ball = turtle.Turtle()
ball.speed(0)
ball.shape("circle")
ball.shapesize(stretch_len=ball_size / 20, stretch_wid=ball_size / 20)
ball.color("white")
ball.penup()
ball.goto(0, 0)

# Sistema de rastro de vento para a bola
wind_trail = []
max_trail_length = 8  # Número máximo de rastros

def create_wind_trail():
    """Cria elementos do rastro de vento"""
    for i in range(max_trail_length):
        trail_element = turtle.Turtle()
        trail_element.speed(0)
        trail_element.shape("circle")
        trail_element.color("white")
        trail_element.penup()
        trail_element.goto(-1000, -1000)  # Posição inicial fora da tela
        wind_trail.append(trail_element)

create_wind_trail()

ball_idx = 0.5
ball_idy = 0.5
ball_idz = 0.5
ball.dx = ball_idx
ball.dy = ball_idy
ball.dz = ball_idz
ball.ax = 0.02
ball.ay = 0.01
ball.az = 0.01
ball.max_dx = 8
ball.max_dy = 2
ball.max_dz = 15
ball.initial_dx = ball_idx # Guarda a velocidade inicial para resetar
ball.initial_dy = ball_idy

score = turtle.Turtle()
score.speed(0)
score.color("white")
score.penup()
score.hideturtle()
score.goto(0,-500)
score.write(f"{score_a}    {score_b}", align="center", font=("Terminal", 50, "normal"))

#divisor
for i in range(6):
    divisor = turtle.Turtle()
    divisor.speed(0)
    divisor.shape("square")
    divisor.shapesize(stretch_len=0.1, stretch_wid= 3 )
    divisor.color("white")
    divisor.penup()
    divisor.goto(0, i*100)

    divisor = turtle.Turtle()
    divisor.speed(0)
    divisor.shape("square")
    divisor.shapesize(stretch_len=0.1, stretch_wid= 3 )
    divisor.color("white")
    divisor.penup()
    divisor.goto(0, - i*100)

# Carregamento dos sons
try:
    fx_player_colide = pygame.mixer.Sound("player_colide.wav")
    fx_silence = pygame.mixer.Sound("silence.wav")
    hit_sound = pygame.mixer.Sound("hit.wav")
    charge_sound = pygame.mixer.Sound("charge.wav")
    point_sound = pygame.mixer.Sound("fall.wav")
    enter_sound = pygame.mixer.Sound("enter.wav")
    speed_sound = pygame.mixer.Sound("speed.wav")
    silence = pygame.mixer.Sound("silence.wav")
except:
    # Se os arquivos de som não existirem, criar sons vazios
    fx_player_colide = None
    fx_silence = None
    hit_sound = None
    charge_sound = None
    point_sound = None
    enter_sound = None
    speed_sound = None
    silence = None

def play_sound(sound):
    """Função auxiliar para tocar som apenas se ele existir"""
    if sound:
        sound.play()

def player1up():
    if player1.ycor() < (wn_height / 2 - 340):    
        player1.sety(player1.ycor() + player1.d)

def player1down():
    if player1.ycor() > (-wn_height / 2 + 340):        
        player1.sety(player1.ycor() - player1.d)

def player1_dash_up():
    """Inicia dash para cima"""
    if player1.dash_cooldown <= 0 and not player1.charge_active:
        player1.dash_active = True
        player1.dash_velocity = player1.dash_initial_speed
        player1.dash_direction = 1  # Para cima
        player1.dash_cooldown = player1.dash_cooldown_time
        player1.color("lightblue")  # Cor visual do dash

def player1_dash_down():
    """Inicia dash para baixo"""
    if player1.dash_cooldown <= 0 and not player1.charge_active:
        player1.dash_active = True
        player1.dash_velocity = player1.dash_initial_speed
        player1.dash_direction = -1  # Para baixo
        player1.dash_cooldown = player1.dash_cooldown_time
        player1.color("lightblue")  # Cor visual do dash

def update_player1_dash():
    """Atualiza o movimento de dash do player1"""
    if player1.dash_active:
        # Calcula nova posição
        new_y = player1.ycor() + (player1.dash_velocity * player1.dash_direction)
        
        # Verifica limites da tela
        if new_y > (wn_height / 2 - 340):
            new_y = wn_height / 2 - 340
            player1.dash_active = False
        elif new_y < (-wn_height / 2 + 340):
            new_y = -wn_height / 2 + 340
            player1.dash_active = False
        
        player1.sety(new_y)
        
        # Aplica desaceleração
        player1.dash_velocity *= player1.dash_decay
        
        # Para o dash quando a velocidade fica muito baixa
        if abs(player1.dash_velocity) < 1:
            player1.dash_active = False
    
    # Atualiza cooldown
    if player1.dash_cooldown > 0:
        player1.dash_cooldown -= 1
    
    # Restaura cor normal quando dash termina
    if not player1.dash_active and not player1.charge_active and player1.color()[0] != (1.0, 1.0, 1.0):
        player1.color("white")

def player1_start_charge():
    player1.charge_active = True
    player1.color("yellow") # Feedback visual de carregamento
    play_sound(charge_sound)

def player1_stop_charge():
    player1.charge_active = False
    player1.color("gray")

def update_player1_charge():
    if player1.charge_active:
        player1.charge_level = min(player1.max_charge, player1.charge_level + player1.charge_rate)
        # Reduz a velocidade normal do player enquanto carrega
        player1.d = player1_ac * 0.5 # Exemplo: metade da velocidade normal
    else:
        # Perde carga gradualmente quando não está carregando
        player1.charge_level = max(0, player1.charge_level - player1.charge_decay_rate)
        player1.d = player1_ac # Restaura velocidade normal

# comandos do jogador
wn.listen()
wn.onkey(player1_dash_up, "w")
wn.onkey(player1_dash_down, "s")
wn.onkeypress(player1_start_charge, "a")
wn.onkeyrelease(player1_stop_charge, "a")

def update_wind_trail():
    """Atualiza o rastro de vento da bola"""
    # Move todos os elementos do rastro uma posição para trás
    for i in range(len(wind_trail) - 1, 0, -1):
        prev_element = wind_trail[i - 1]
        current_element = wind_trail[i]
        
        # Copia posição e tamanho do elemento anterior
        current_element.goto(prev_element.xcor(), prev_element.ycor())
        current_element.shapesize(prev_element.shapesize()[0] * 0.9, prev_element.shapesize()[1] * 0.9)
        
        # Reduz a opacidade (simulado com cores mais claras)
        opacity = 1.0 - (i / len(wind_trail))
        if opacity > 0.1:
            current_element.showturtle()
            # Gradiente de cor baseado na velocidade da bola
            speed_factor = min(0.01, (abs(ball.dx) + abs(ball.dy)) / 15)
            if speed_factor > 0.7:
                current_element.color("lightblue")
            elif speed_factor > 0.4:
                current_element.color("white")
            else:
                current_element.color("white")
        else:
            current_element.hideturtle()
    
    # Atualiza o primeiro elemento do rastro com a posição atual da bola
    if wind_trail:
        wind_trail[0].goto(ball.xcor(), ball.ycor())
        wind_trail[0].shapesize(ball.shapesize()[0] * 1, ball.shapesize()[1] * 1)
        wind_trail[0].showturtle()

def ball_movement():
    global ball_size

    # Implementa curvas para evitar paredes
    # Quando a bola se aproxima das paredes, ela tenta fazer uma curva
    wall_proximity_threshold = 280  # Distância da parede para começar a curva
    curve_strength = 0.2  # Força da curva
    
    # Verifica proximidade com parede superior
    if ball.ycor() > (wn_height/2 - wall_proximity_threshold) and ball.dy > 0:
        # Aplica uma força para baixo (curva para evitar a parede)
        ball.dy -= curve_strength
        ball.ay -= curve_strength * 0.1
    
    # Verifica proximidade com parede inferior
    elif ball.ycor() < (-wn_height/2 + wall_proximity_threshold) and ball.dy < 0:
        # Aplica uma força para cima (curva para evitar a parede)
        ball.dy += curve_strength
        ball.ay += curve_strength * 0.1

    #aceleração direita
    if ball.dx > 0:
        if ball.dx < ball.max_dx:
            ball.dx += ball.ax
        
    #aceleração esquerda
    if ball.dx < 0:
        if ball.dx > -ball.max_dx:
            ball.dx -= ball.ax
    
    if ball.dx > 0:
        if ball.dy < ball.max_dy:
            ball.dy += ball.ay

    if ball.dx < 0:
        if ball.dy < -ball.max_dy:
            ball.dy -= ball.ay
    
    #aceleração z
    if ball.dz < ball.max_dz:
        ball.dz += ball.az

    #ball movement
    ball.setx(ball.xcor()+ball.dx)    
    ball.sety(ball.ycor()+ball.dy)    
    
    #ball jump (simulação 3D)
    # O tamanho da bola agora depende da distância horizontal do centro, do ângulo de acerto e condições especiais
    # Isso simula um arco tridimensional
    distance_from_center_x = abs(ball.xcor())
    max_distance_x = wn_widht / 2
    
    # Normaliza a distância para um valor entre 0 e 1
    normalized_distance = distance_from_center_x / max_distance_x
    
    # Calcula o ângulo da trajetória da bola
    trajectory_angle = math.atan2(ball.dy, ball.dx) if ball.dx != 0 else 0
    angle_factor = abs(math.sin(trajectory_angle)) # Quanto mais vertical, maior o efeito 3D
    
    # Ajusta o tamanho da bola baseado na distância, ângulo e velocidade
    # Quanto mais perto do centro, menor (como se estivesse mais longe no Z)
    # Quanto mais perto das bordas X, maior (como se estivesse mais perto no Z)
    # Ângulos mais verticais criam efeito 3D mais pronunciado
    base_size_factor = normalized_distance * 295
    angle_size_factor = angle_factor * 300 # Efeito adicional baseado no ângulo
    velocity_factor = (abs(ball.dx) + abs(ball.dy)) * -13.5 # Efeito baseado na velocidade
    
    ball.size = base_size_factor + angle_size_factor + velocity_factor + ball_size 
    
    # Limita o tamanho da bola para evitar valores extremos
    ball.size = max(29, min(ball.size, 152))


    ball.shapesize(stretch_len=ball.size / 20 , stretch_wid=ball.size / 20 )
    
    # Atualiza o rastro de vento
    update_wind_trail()


def player_angle():
    player1.setheading(-player1.ycor() * 0.04)

def update_player2_dash():
    """Atualiza o movimento de dash do player2 (IA)"""
    if player2.dash_active:
        # Calcula nova posição
        new_y = player2.ycor() + (player2.dash_velocity * player2.dash_direction)
        
        # Verifica limites da tela
        if new_y > (wn_height / 2 - 340):
            new_y = wn_height / 2 - 340
            player2.dash_active = False
        elif new_y < (-wn_height / 2 + 340):
            new_y = -wn_height / 2 + 340
            player2.dash_active = False
        
        player2.sety(new_y)
        
        # Aplica desaceleração
        player2.dash_velocity *= player2.dash_decay
        
        # Para o dash quando a velocidade fica muito baixa
        if abs(player2.dash_velocity) < 1:
            player2.dash_active = False
    
    # Atualiza cooldown
    if player2.dash_cooldown > 0:
        player2.dash_cooldown -= 1
    
    # Restaura cor normal quando dash termina
    if not player2.dash_active and player2.color()[0] != (1.0, 1.0, 1.0):
        player2.color("white")

def update_player2_ai():
    # Player 2 tenta seguir a bola
    target_y = ball.ycor()
    
    # Calcula a diferença entre a posição da bola e a do player 2
    y_diff = target_y - player2.ycor()
    
    # Verifica se deve usar dash (quando a bola está longe e se aproximando)
    if (player2.dash_cooldown <= 0 and not player2.dash_active and 
        abs(y_diff) > player2.dash_trigger_distance and ball.dx > 0):  # Bola vindo em direção ao player 2
        
        # Ativa dash na direção da bola
        player2.dash_active = True
        player2.dash_velocity = player2.dash_initial_speed
        player2.dash_direction = 1 if y_diff > 0 else -1
        player2.dash_cooldown = player2.dash_cooldown_time
        player2.color("red")  # Cor visual do dash da IA
    
    # Se não estiver em dash, usa movimento normal
    if not player2.dash_active:
        # Se a bola estiver longe, acelera mais rápido
        if abs(y_diff) > 50: # Limiar para aceleração forte
            player2.current_speed += player2.acceleration * 2 # Aceleração mais forte
        else:
            player2.current_speed += player2.acceleration # Aceleração normal

        # Limita a velocidade atual
        player2.current_speed = min(player2.current_speed, player2.max_speed)
        player2.current_speed = max(player2.current_speed, player2.min_speed)

        # Move o player 2 em direção à bola
        if y_diff > 0: # Bola acima do player 2
            new_y = player2.ycor() + player2.current_speed
        else: # Bola abaixo do player 2
            new_y = player2.ycor() - player2.current_speed

        # Garante que o player 2 não saia dos limites da tela
        if new_y > (wn_height / 2 - 340):
            new_y = wn_height / 2 - 340
            player2.current_speed = player2.min_speed # Reduz velocidade ao atingir limite
        elif new_y < (-wn_height / 2 + 340):
            new_y = -wn_height / 2 + 340
            player2.current_speed = player2.min_speed # Reduz velocidade ao atingir limite

        player2.sety(new_y)

def game_loop():
    global score_a
    global score_b
    global player1_ac
    global ball_idx
    
    wn.update()    

    # Atualiza dash do player1
    update_player1_dash()
    # Atualiza carga do player1
    update_player1_charge()
    # Atualiza dash do player2 (IA)
    update_player2_dash()
    
    ball_movement()
    player_angle()
    update_player2_ai()


    # border checking 
    if ball.ycor() > wn_height/2-280:        
        ball.sety(wn_height/2-280)
        ball.dy *= -1
        ball.ay *= -1
        ball.dx *= 0.95 # Perde velocidade ao colidir com parede
        ball.dy *= 0.95 # Perde velocidade ao colidir com parede
        play_sound(hit_sound)

    if ball.ycor() < -wn_height/2+280:        
        ball.sety(-wn_height/2+280)
        ball.dy *= -1
        ball.ay *= -1
        ball.dx *= 0.95 # Perde velocidade ao colidir com parede
        ball.dy *= 0.95 # Perde velocidade ao colidir com parede
        play_sound(hit_sound)

    # player 1 scores
    if ball.xcor() > wn_widht/2 :
        ball.goto(0,0)
        player2.goto(wn_widht/2 -player_recuo, 0)
        player1.goto(-wn_widht/2 +player_recuo, 0)
        ball.dx = -ball.initial_dx # Reinicia aceleração
        ball.dy = ball.initial_dy
        score_a += 1
        score.clear()
        score.write(f"{score_a}    {score_b}", align="center", font=("Terminal", 50, "normal"))
        play_sound(point_sound)
        
    # player 2 scores
    if ball.xcor() < -wn_widht/2 :
        ball.goto(0,0)   
        player2.goto(wn_widht/2 -player_recuo, 0)
        player1.goto(-wn_widht/2 +player_recuo, 0)
        ball.dx = ball.initial_dx # Reinicia aceleração
        ball.dy = ball.initial_dy
        score_b += 1
        score.clear()
        score.write(f"{score_a}    {score_b}", align="center", font=("Terminal", 50, "normal"))
        play_sound(point_sound)
        
    # Função auxiliar para verificar colisão entre bola e raquete
    def check_collision(ball, player, effective_player_width, effective_player_height):
        # Considera a posição central da raquete e da bola
        ball_left = ball.xcor() - ball.size / 2
        ball_right = ball.xcor() + ball.size / 2
        ball_top = ball.ycor() + ball.size / 2
        ball_bottom = ball.ycor() - ball.size / 2

        player_left = player.xcor() - effective_player_width / 2
        player_right = player.xcor() + effective_player_width / 2
        player_top = player.ycor() + effective_player_height / 2
        player_bottom = player.ycor() - effective_player_height / 2

        # Verifica sobreposição nos eixos X e Y
        if (ball_right > player_left and ball_left < player_right and
            ball_top > player_bottom and ball_bottom < player_top):
            return True
        return False

    # Calcula área de colisão expandida durante dash
    collision_height_multiplier = 2.0 if player1.dash_active else 1.0
    collision_width_multiplier = 1.5 if player1.dash_active else 1.0
    effective_player_height = player_height * collision_height_multiplier
    effective_player_width = player_width * collision_width_multiplier

    # colisões de player
    # esquerdo - com área de colisão expandida durante dash
    if ball.dx < 0 and check_collision(ball, player1, effective_player_width, effective_player_height):
        
        # Calcula o ponto de impacto relativo ao centro do player
        impact_point = (ball.ycor() - player1.ycor()) / (effective_player_height / 2)
        
        ball.dx *= -1 # Inverte direção
        ball.dx *= 0.95 # Perde velocidade ao colidir com player
        ball.dy *= 0.95 # Perde velocidade ao colidir com player

        # Se estiver em dash, adiciona efeitos especiais
        if player1.dash_active:
            # Adiciona spin baseado na direção do dash e ponto de impacto
            ball.dy += player1.dash_direction * 3 + impact_point * 1.5
            # Adiciona velocidade extra horizontal
            ball.dx *= 1.3
            play_sound(charge_sound)
            
            # Efeito visual temporário

        elif player1.charge_active: # Se estiver carregando impulso
            # Aumenta a aceleração da bola de acordo com o nível de carga e ângulo de acerto
            charge_boost = player1.charge_level / player1.max_charge * 5 # Ajuste o multiplicador conforme necessário
            ball.dx *= (1 + charge_boost * abs(impact_point)) # Mais boost se acertar na ponta
            ball.dy += impact_point * charge_boost * 2 # Mais spin com carga
            play_sound(charge_sound)
            player1.charge_level = 0 # Reseta a carga após o uso
            player1.color("white")
        else:
            # Efeito normal baseado no ponto de impacto
            ball.dy += impact_point * 1.0
        
        play_sound(hit_sound)
        play_sound(enter_sound)

    #direito - com área de colisão expandida durante dash da IA
    collision_height_multiplier_p2 = 1.8 if player2.dash_active else 1.0
    collision_width_multiplier_p2 = 1.3 if player2.dash_active else 1.0
    effective_player_height_p2 = player_height * collision_height_multiplier_p2
    effective_player_width_p2 = player_width * collision_width_multiplier_p2
    
    if ball.dx > 0 and check_collision(ball, player2, effective_player_width_p2, effective_player_height_p2):
        # Calcula o ponto de impacto relativo ao centro do player
        impact_point = (ball.ycor() - player2.ycor()) / (effective_player_height_p2 / 2)
        
        ball.dx *= -1 # Inverte direção
        ball.dx *= 0.95 # Perde velocidade ao colidir com player
        ball.dy *= 0.95 # Perde velocidade ao colidir com player
        
        # Se a IA estiver em dash, adiciona efeitos especiais
        if player2.dash_active:
            # Adiciona spin baseado na direção do dash e ponto de impacto
            ball.dy += player2.dash_direction * 2.5 + impact_point * 1.2
            # Adiciona velocidade extra horizontal (menor que o jogador 1)
            ball.dx *= 1.2
            play_sound(charge_sound)
            
            # Efeito visual temporário

        else:
            # Efeito normal baseado no ponto de impacto
            ball.dy += impact_point * 0.8
        
        play_sound(hit_sound)
        play_sound(enter_sound)

    wn.ontimer(game_loop, 5)

game_loop()
wn.mainloop()

