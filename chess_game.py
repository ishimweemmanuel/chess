import pygame
import chess
import sys
import os
from typing import Tuple, List, Optional
from stockfish import Stockfish

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 900  # Increased window size to accommodate names
BOARD_SIZE = 700
SQUARE_SIZE = BOARD_SIZE // 8
PIECE_SIZE = SQUARE_SIZE - 10
FPS = 60

# Colors


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
YELLOW = (204, 204, 0)
BLUE = (50, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WHITE
        self.text = text
        self.font = pygame.font.Font(None, 32)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = GREEN if self.active else WHITE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.color)
        return None

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

class ChessGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self.board = chess.Board()
        
        # Initialize Stockfish engine
        try:
            self.stockfish = Stockfish(parameters={"Threads": 2, "Minimum Thinking Time must be this ": 30})
            self.has_engine = True
        except Exception as e:
            print(f"Warning: Stockfish engine not available: {e}")
            self.has_engine = False
        
        # Load pieces images
        self.pieces_images = {}
        self.load_pieces()
        
        self.selected_square = None
        self.valid_moves = []
        self.game_mode = self.select_game_mode()  # Get game mode from menu
        self.player_color = chess.WHITE if self.game_mode != 'ai_vs_player' else chess.BLACK
        self.show_game_over = False
        self.game_over_message = ""
        
        # Player names
        self.player_name = self.get_player_name()
        self.ai_name = "Stockfish AI"
        self.player2_name = self.get_player2_name() if self.game_mode == 'player_vs_player' else "Player 2"
        
        # Font for displaying names
        self.name_font = pygame.font.Font(None, 36)
        
        # Make AI move if it's AI's turn at the start
        if self.game_mode == 'ai_vs_player':
            self.make_ai_move()

    def get_player_name(self) -> str:
        input_box = InputBox(WINDOW_SIZE//2 - 100, WINDOW_SIZE//2 - 20, 200, 40)
        prompt_font = pygame.font.Font(None, 36)
        prompt_text = prompt_font.render("Enter Your name:", True, WHITE)
        prompt_rect = prompt_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 50))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                name = input_box.handle_event(event)
                if name:
                    return name if name.strip() else "Player No 1"
            
            self.screen.fill(BLACK)
            self.screen.blit(prompt_text, prompt_rect)
            input_box.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

    def get_player2_name(self) -> str:
        self.screen.fill(BLACK)
        input_box = InputBox(WINDOW_SIZE//2 - 100, WINDOW_SIZE//2 - 20, 200, 40)
        prompt_font = pygame.font.Font(None, 36)
        prompt_text = prompt_font.render("Enter Player 2's name:", True, WHITE)
        prompt_rect = prompt_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 50))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                name = input_box.handle_event(event)
                if name:
                    return name if name.strip() else "Player 2"
            
            self.screen.fill(BLACK)
            self.screen.blit(prompt_text, prompt_rect)
            input_box.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

    def select_game_mode(self) -> str:
        modes = ['player_vs_ai', 'ai_vs_player', 'player_vs_player']
        mode_texts = ['Play as White vs AI', 'Play as Black vs AI', 'Play vs Another Player']
        selected = 0
        font = pygame.font.Font(None, 36)
        
        while True:
            self.screen.fill(BLACK)
            title = font.render("Select Game Mode you want ", True, WHITE)
            title_rect = title.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//4))
            self.screen.blit(title, title_rect)
            
            for i, text in enumerate(mode_texts):
                color = GREEN if i == selected else WHITE
                text_surface = font.render(text, True, color)
                text_rect = text_surface.get_rect(
                    center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + i * 50)
                )
                self.screen.blit(text_surface, text_rect)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(modes)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(modes)
                    elif event.key == pygame.K_RETURN:
                        return modes[selected]
            
            instruction = font.render("Use ↑↓ to select, Enter to confirm", True, GRAY)
            instruction_rect = instruction.get_rect(
                center=(WINDOW_SIZE//2, WINDOW_SIZE * 3//4)
            )
            self.screen.blit(instruction, instruction_rect)
            
            pygame.display.flip()
            self.clock.tick(FPS)

    def load_pieces(self):
        pieces = ['p', 'r', 'n', 'b', 'q', 'k']
        for piece in pieces:
            # Load white pieces
            self.pieces_images[piece.upper()] = pygame.transform.scale(
                pygame.image.load(f"pieces/w_{piece}.png"),
                (PIECE_SIZE, PIECE_SIZE)
            )
            # Load black pieces
            self.pieces_images[piece] = pygame.transform.scale(
                pygame.image.load(f"pieces/b_{piece}.png"),
                (PIECE_SIZE, PIECE_SIZE)
            )

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                x = col * SQUARE_SIZE + (WINDOW_SIZE - BOARD_SIZE) // 2
                y = row * SQUARE_SIZE + (WINDOW_SIZE - BOARD_SIZE) // 2
                color = WHITE if (row + col) % 2 == 0 else GRAY
                pygame.draw.rect(self.screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self):
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                x = chess.square_file(square) * SQUARE_SIZE + (WINDOW_SIZE - BOARD_SIZE) // 2
                y = (7 - chess.square_rank(square)) * SQUARE_SIZE + (WINDOW_SIZE - BOARD_SIZE) // 2
                piece_symbol = piece.symbol()
                if piece_symbol in self.pieces_images:
                    self.screen.blit(
                        self.pieces_images[piece_symbol],
                        (x + 5, y + 5)
                    )

    def highlight_squares(self):
        if self.selected_square is not None:
            x = chess.square_file(self.selected_square) * SQUARE_SIZE + (WINDOW_SIZE - BOARD_SIZE) // 2
            y = (7 - chess.square_rank(self.selected_square)) * SQUARE_SIZE + (WINDOW_SIZE - BOARD_SIZE) // 2
            pygame.draw.rect(self.screen, YELLOW, (x, y, SQUARE_SIZE, SQUARE_SIZE), 3)

        for move in self.valid_moves:
            x = chess.square_file(move.to_square) * SQUARE_SIZE + (WINDOW_SIZE - BOARD_SIZE) // 2
            y = (7 - chess.square_rank(move.to_square)) * SQUARE_SIZE + (WINDOW_SIZE - BOARD_SIZE) // 2
            pygame.draw.rect(self.screen, BLUE, (x, y, SQUARE_SIZE, SQUARE_SIZE), 3)

    def draw_game_over(self):
        if self.show_game_over:
            font = pygame.font.Font(None, 36)
            text = font.render(self.game_over_message, True, GREEN, BLACK)
            text_rect = text.get_rect(center=(WINDOW_SIZE/2, WINDOW_SIZE/2))
            self.screen.blit(text, text_rect)
    def get_square_from_pos(self, pos: Tuple[int, int]) -> Optional[int]:
        x, y = pos
        x -= (WINDOW_SIZE - BOARD_SIZE) // 2
        y -= (WINDOW_SIZE - BOARD_SIZE) // 2
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            file = x // SQUARE_SIZE
            rank = 7 - (y // SQUARE_SIZE)
            return chess.square(file, rank)
        return None

    def get_valid_moves(self, square: int) -> List[chess.Move]:
        valid_moves = []
        for move in self.board.legal_moves:
            if move.from_square == square:
                valid_moves.append(move)
        return valid_moves

    def make_ai_move(self):
        if not self.has_engine:
            # Fallback to random move if Stockfish is not available
            legal_moves = list(self.board.legal_moves)
            if legal_moves:
                import random
                move = random.choice(legal_moves)
                self.board.push(move)
            return

        # Set up the position for Stockfish
        self.stockfish.set_position([move.uci() for move in self.board.move_stack])
        
        # Get the best move from Stockfish
        best_move = self.stockfish.get_best_move()
        if best_move:
            self.board.push(chess.Move.from_uci(best_move))

    def check_game_over(self):
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            winner_name = self.get_player_name_by_color(winner.lower() == "white")
            self.game_over_message = f"{winner_name} wins by checkmate!"
            self.show_game_over = True
        elif self.board.is_stalemate():
            self.game_over_message = "Game drawn by stalemate!"
            self.show_game_over = True
        elif self.board.is_insufficient_material():
            self.game_over_message = "Game drawn by insufficient material!"
            self.show_game_over = True

    def get_player_name_by_color(self, is_white: bool) -> str:
        if self.game_mode == 'player_vs_ai':
            if (is_white and self.player_color == chess.WHITE) or (not is_white and self.player_color == chess.BLACK):
                return self.player_name
            return self.ai_name
        elif self.game_mode == 'ai_vs_player':
            if (is_white and self.player_color == chess.WHITE) or (not is_white and self.player_color == chess.BLACK):
                return self.player_name
            return self.ai_name
        else:  # player_vs_player
            return self.player_name if is_white else self.player2_name

    def draw_player_names(self):
        # Draw names based on game mode and current turn
        if self.game_mode == 'player_vs_ai':
            # White player (bottom)
            if self.player_color == chess.WHITE:
                bottom_name = self.player_name
                top_name = self.ai_name
            else:
                bottom_name = self.ai_name
                top_name = self.player_name
        elif self.game_mode == 'ai_vs_player':
            if self.player_color == chess.WHITE:
                bottom_name = self.player_name
                top_name = self.ai_name
            else:
                bottom_name = self.ai_name
                top_name = self.player_name
        else:  # player_vs_player
            bottom_name = self.player_name
            top_name = self.player2_name

        # Highlight active player
        bottom_color = GREEN if self.board.turn == chess.WHITE else WHITE
        top_color = GREEN if self.board.turn == chess.BLACK else WHITE

        # Render names
        bottom_text = self.name_font.render(f"{bottom_name} (White)", True, bottom_color)
        top_text = self.name_font.render(f"{top_name} (Black)", True, top_color)

        # Position names
        bottom_rect = bottom_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE - 30))
        top_rect = top_text.get_rect(center=(WINDOW_SIZE//2, 30))

        # Draw names
        self.screen.blit(bottom_text, bottom_rect)
        self.screen.blit(top_text, top_rect)

    def handle_click(self, pos: Tuple[int, int]):
        square = self.get_square_from_pos(pos)
        if square is None:
            return

        # If it's AI's turn, ignore clicks
        if ((self.game_mode == 'player_vs_ai' and not self.board.turn == self.player_color) or
            (self.game_mode == 'ai_vs_player' and self.board.turn == self.player_color)):
            return

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self.valid_moves = self.get_valid_moves(square)
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.valid_moves:
                self.board.push(move)
                self.check_game_over()
                
                # Make AI move if it's AI's turn
                if not self.show_game_over and (
                    (self.game_mode == 'player_vs_ai' and not self.board.turn == self.player_color) or
                    (self.game_mode == 'ai_vs_player' and self.board.turn == self.player_color)):
                    self.make_ai_move()
                    self.check_game_over()
            
            self.selected_square = None
            self.valid_moves = []

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        # Reset game with new mode selection
                        self.game_mode = self.select_game_mode()
                        self.player_color = chess.WHITE if self.game_mode != 'ai_vs_player' else chess.BLACK
                        if self.game_mode == 'player_vs_player':
                            self.player2_name = self.get_player2_name()
                        self.board.reset()
                        self.show_game_over = False
                        self.selected_square = None
                        self.valid_moves = []
                        # Make AI move if it's AI's turn at the start
                        if self.game_mode == 'ai_vs_player':
                            self.make_ai_move()
                    elif event.key == pygame.K_r:
                        self.board.reset()
                        self.show_game_over = False
                        self.selected_square = None
                        self.valid_moves = []
                        # Make AI move if it's AI's turn at the start
                        if self.game_mode == 'ai_vs_player':
                            self.make_ai_move()
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            self.screen.fill(BLACK)
            self.draw_board()
            self.highlight_squares()
            self.draw_pieces()
            self.draw_player_names()  # Draw player names
            self.draw_game_over()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()
