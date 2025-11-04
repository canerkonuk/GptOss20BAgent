"""
Main entry point for GPT-OSS-20B Agent
Initializes the model and launches the Gradio UI
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(__file__))

from src.agent import get_agent
from src.ui import launch_ui
import config


def main():
    """Main function to run the application"""

    print("=" * 60)
    print("GPT-OSS-20B Agent")
    print("=" * 60)
    print()

    # Check model file
    print("Checking for model file...")
    model_info = config.get_model_info()

    if not model_info["exists"]:
        print(f"❌ ERROR: Model file not found!")
        print(f"Expected location: {model_info['path']}")
        print()
        print("Please follow these steps:")
        print("1. Download gpt-oss-20b-Q5_K_M.gguf from:")
        print("   https://huggingface.co/unsloth/gpt-oss-20b-GGUF")
        print("2. Place it in the 'models/' directory")
        print("3. Run this script again")
        print()
        input("Press Enter to exit...")
        sys.exit(1)

    print(f"✅ Model found: {model_info['size_mb']} MB")
    print()

    # Initialize agent
    print("Initializing AI Agent...")
    agent = get_agent()

    # Load model
    print("Loading model (this may take a minute)...")
    success, message = agent.load_model()

    if not success:
        print(f"❌ ERROR: {message}")
        print()
        print("Possible issues:")
        print("- Not enough RAM (need ~15GB for model)")
        print("- Corrupted model file")
        print("- Missing dependencies")
        print()
        input("Press Enter to exit...")
        sys.exit(1)

    print(f"✅ {message}")
    print()

    # Launch UI
    print("Starting Gradio interface...")
    print(f"Server will run on: http://{config.GRADIO_CONFIG['server_name']}:{config.GRADIO_CONFIG['server_port']}")
    print()
    print("=" * 60)
    print("Application is ready! Opening in your browser...")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()

    try:
        launch_ui()
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        print("Goodbye!")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nThe application encountered an error.")
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
