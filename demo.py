#!/usr/bin/env python3
"""
Demo Script - Interactive demonstration of World Engine capabilities.
"""

from api.service import WorldEngineAPI


def main():
    """Run interactive demo."""
    print("=" * 60)
    print("World Engine - Semantic Analysis Demo")
    print("=" * 60)
    
    # Initialize engine
    engine = WorldEngineAPI()
    
    print("\n📚 Loaded Seeds:")
    for word, value in sorted(engine.seed_manager.seeds.items(), key=lambda x: x[1]):
        print(f"  {word:15s} → {value:+.2f}")
    
    print("\n🔗 Constraint Validation:")
    violations = engine.seed_manager.validate_constraints()
    if violations:
        print("  ❌ Violations found:")
        for v in violations:
            print(f"     {v}")
    else:
        print("  ✅ All constraints satisfied")
    
    # Demo texts
    demo_texts = [
        "This is an excellent product with wonderful features!",
        "The terrible experience left me feeling awful.",
        "It was an average day, nothing special.",
    ]
    
    print("\n📝 Demo Text Analysis:")
    for i, text in enumerate(demo_texts, 1):
        print(f"\n{i}. \"{text}\"")
        result = engine.analyze_text(text)
        
        print(f"   Sentiment Score: {result['sentiment_score']:+.2f}")
        print(f"   Keywords: {', '.join(result['keywords'][:5])}")
        print(f"   Entities: {', '.join(e['text'] for e in result['entities']) or 'None'}")
    
    # Interactive mode
    print("\n" + "=" * 60)
    print("Interactive Mode - Enter text to analyze (or 'quit' to exit)")
    print("=" * 60)
    
    while True:
        try:
            text = input("\n> ").strip()
            if text.lower() in ("quit", "exit", "q"):
                break
            if not text:
                continue
            
            result = engine.analyze_text(text)
            print(f"\n  Sentiment: {result['sentiment_score']:+.2f}")
            print(f"  Keywords: {', '.join(result['keywords'][:8])}")
            
            # Show matched seed words
            matched_seeds = [
                (token['lemma'], engine.seed_manager.get_seed(token['lemma']))
                for token in result['tokens']
                if engine.seed_manager.get_seed(token['lemma']) is not None
            ]
            if matched_seeds:
                print(f"  Matched Seeds: {', '.join(f'{w}({v:+.1f})' for w, v in matched_seeds)}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n👋 Demo complete!")


if __name__ == "__main__":
    main()
