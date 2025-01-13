import os
import requests
import sys

def download_pieces():
    # Create pieces directory if it doesn't exist
    pieces_dir = os.path.join(os.path.dirname(__file__), 'pieces')
    if not os.path.exists(pieces_dir):
        os.makedirs(pieces_dir)
        print(f"Created directory: {pieces_dir}")

    # Dictionary of piece images (using PNG files directly)
    piece_urls = {
        'w_p': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wp.png',
        'w_r': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wr.png',
        'w_n': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wn.png',
        'w_b': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wb.png',
        'w_q': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wq.png',
        'w_k': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wk.png',
        'b_p': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bp.png',
        'b_r': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/br.png',
        'b_n': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bn.png',
        'b_b': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bb.png',
        'b_q': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bq.png',
        'b_k': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bk.png'
    }

    success_count = 0
    for piece_name, url in piece_urls.items():
        try:
            print(f"Downloading {piece_name}...", end=" ")
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            filepath = os.path.join(pieces_dir, f"{piece_name}.png")
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"Success! Saved to {filepath}")
            success_count += 1
            
        except Exception as e:
            print(f"Failed! Error: {str(e)}")

    print(f"\nDownloaded {success_count} out of {len(piece_urls)} pieces.")
    return success_count == len(piece_urls)

if __name__ == "__main__":
    print("Starting chess piece download...")
    if download_pieces():
        print("All pieces downloaded successfully!")
        sys.exit(0)
    else:
        print("Some pieces failed to download. Please try again.")
        sys.exit(1)
