#!/usr/bin/env python3
"""
Fresh World Engine - Main Entry Point
"""

import pygame
import sys
from engine.core import Engine

def main():
    """Main function to start the engine."""
    pygame.init()

    # Initialize the engine
    engine = Engine()

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update engine
        engine.update()

        # Render
        engine.render()

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()