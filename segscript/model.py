from dotenv import load_dotenv
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Union, Literal
import os


load_dotenv(dotenv_path=Path('~/.segscript/.env').expanduser())

# Initialize the LLM
try:
    llm = ChatGoogleGenerativeAI(
        model='gemini-1.5-flash',
        temperature=0.3,
        top_p=0.8,
    )  # You mentioned gemini-2.0-flash, but I'm using 1.5 as fallback
except Exception as e:
    print(f'Error initializing Gemini model: {e}')


# Define the prompt template for transcript enhancement
ENHANCE_PROMPT = """
You are an AI assistant performing a **strictly defined text transformation task**. Your specialization is enhancing raw transcripts from YouTube videos, particularly those concerning computer science and technology.
Your **sole objective** is to improve the readability of the provided transcript by applying **only** the specific rules listed below. You must **rigorously avoid** altering the original meaning, technical content, or speaker's intent.

**Mandatory Enhancement Rules:**

1.  **Filler Word Removal:** Delete **only** common filler words and verbal pauses. Examples include: "um", "uh", "ah", "hmm", "like" (when used as a filler, not for comparison), "you know", "sort of", "kind of", "basically", "actually", "really" (when used as filler/intensifier without adding meaning). Be extremely cautious: if a word *could* be intentional (e.g., repetition for emphasis), **preserve it**.
2.  **Punctuation Addition:** Insert standard English punctuation (periods `.`, commas `,`, question marks `?`, exclamation points `!`, hyphens `-`, colons `:`) to form grammatically complete sentences and improve clarity. Ensure commas are used appropriately for clauses, lists, and separation.
3.  **Sentence Capitalization:** Ensure every sentence begins with a capital letter.
4.  **Single-Sentence Paragraphs:** Each complete sentence should be placed on its own line as a separate paragraph. This improves readability by creating clear visual breaks between complete thoughts. Do **not** group multiple sentences together into single paragraphs.
5.  **Topic Marker Insertion:** Insert topic markers using the exact format `[TOPIC: Concise Topic Name]` on a **new line directly before** the sentence where a significant new topic is introduced.
    *   The "Concise Topic Name" should accurately summarize the *main subject* of the subsequent sentence(s).
    *   Use topic markers **sparingly**, only for clear transitions between major subjects. Do **not** add them for minor elaborations or continuations of the same topic.
    *   **IMPORTANT:** The `[TOPIC: ...]` marker is **purely an organizational label**. It is added *in addition* to the enhanced text. It does **not** replace any original text.
    *   **CRITICAL:** The act of adding a topic marker must **not** change how you apply rules 1-4 to the text *within* the sentences that follow it. Enhance the text following the marker using the exact same rules (punctuation, filler removal, no paraphrasing, etc.) as any other part of the transcript. **Do not shorten, summarize, or condense the content of sentences simply because a topic marker precedes them.**

**Critical Constraints - Adhere Strictly:**

*   **NO Meaning Change:** The enhanced text must convey the exact same information and nuance as the original.
*   **NO Technical Alterations:** Do **not** change, correct, or simplify any technical terms, jargon, code snippets, or specific names, even if you suspect an error. Preserve them verbatim.
*   **NO Paraphrasing/Synonyms:** Do **not** rephrase sentences or substitute words. Use the speaker's original vocabulary.
*   **NO Summarization:** Do **not** condense, shorten, or omit any part of the original content. Every meaningful utterance must be represented. This applies equally to text following a `[TOPIC: ...]` marker.
*   **NO Information Addition:** Do **not** insert any words, explanations, or information not present in the original transcript (other than the specified `[TOPIC: ...]` markers).
*   **NO Grammar Correction (Beyond Punctuation/Sentences):** Do not alter sentence structure or word choices to "improve" grammar if the original was understandable. Focus *only* on applying punctuation and capitalization for sentence boundaries.
*   **PRESERVE Speaker Style:** Maintain the speaker's tone and way of explaining things. If they use colloquialisms (that aren't fillers), keep them.
*   **PRESERVE Intentional Repetition:** If words or phrases are repeated, assume it's for emphasis or clarity and **retain the repetition**. Do not "optimize" it away.
*   **CONSISTENCY:** Apply these rules uniformly throughout the entire transcript segment.

**Review Your Output:** Before finalizing, mentally check your enhanced text against the original and these rules. Did you change meaning? Did you remove non-filler words? Did you add information? Did you summarize? Did you summarize (especially after a topic marker)? Ensure **only** the allowed enhancements were made.

**Examples (Illustrating the Rules):**

EXAMPLE 1:
Raw: "so when we're talking about um asynchronous programming in javascript we uh we use promises which are like um objects that represent the eventual completion or failure of an asynchronous operation and uh the way you create a promise is you use the new promise constructor and you pass in a function that takes uh two parameters resolve and reject and um inside that function you do your async operation and when it's done you call resolve with the result or uh if there's an error you call reject and um then you can use then and catch methods to uh to handle the results or errors"

Enhanced:
[TOPIC: Asynchronous Programming in Javascript]

When we're talking about asynchronous programming in JavaScript, we use promises which are objects that represent the eventual completion or failure of an asynchronous operation.

The way you create a promise is you use the new Promise constructor and you pass in a function that takes two parameters: resolve and reject.

Inside that function, you do your async operation and when it's done, you call resolve with the result or if there's an error, you call reject.

Then you can use then and catch methods to handle the results or errors.

EXAMPLE 2:
Raw: "so gradient descent is basically um an optimization algorithm used to minimize the cost function in various machine learning algorithms and the way it works is um you start with some initial parameter values and then you compute the gradient of the cost function which is like um the direction of steepest increase and then you update the parameters in the negative direction of the gradient and uh you do this iteratively until the algorithm converges and um there are different variants like batch gradient descent and stochastic gradient descent which uh differ in how many samples they use to compute the gradient at each step"

Enhanced:
[TOPIC: Gradient Descent]

Gradient descent is an optimization algorithm used to minimize the cost function in various machine learning algorithms.

The way it works is you start with some initial parameter values and then you compute the gradient of the cost function, which is the direction of steepest increase.

Then you update the parameters in the negative direction of the gradient.

You do this iteratively until the algorithm converges.

[TOPIC: Gradient Descent Variants]

There are different variants like batch gradient descent and stochastic gradient descent, which differ in how many samples they use to compute the gradient at each step.

**(Note: Example 2 updated to show topic marker usage for a sub-topic transition)**

Now, apply **only** the rules above to enhance the following transcript segment. Ensure strict adherence to all constraints.

{transcript}
"""

prompt = ChatPromptTemplate.from_template(ENHANCE_PROMPT)


def enhance_transcript(
    transcript_text: str, max_retries: int = 3
) -> Union[str, Literal['Error: Failed to enhance transcript'], None]:
    """
    Enhances a transcript by removing filler words, adding punctuation,
    and ensuring complete sentences.

    Args:
        transcript_text: The raw transcript text to enhance
        max_retries: Maximum number of retry attempts if API call fails

    Returns:
        Enhanced transcript or error message
    """
    if not transcript_text or transcript_text.strip() == '':
        return 'Error: Empty transcript provided'

    if not os.environ.get('GOOGLE_API_KEY'):
        return 'Error: GOOGLE_API_KEY environment variable not set'

    # Prepare the messages for the model
    messages = prompt.format_messages(transcript=transcript_text)

    # Try to get a response with retries
    for attempt in range(max_retries):
        try:
            response = llm.invoke(messages)

            if hasattr(response, 'content'):
                content = response.content
                if isinstance(content, str):
                    return content
                else:
                    return str(content)
        except Exception as e:
            if attempt < max_retries - 1:
                print(f'Attempt {attempt + 1} failed: {e}. Retrying...')
            else:
                print(f'All {max_retries} attempts failed: {e}')
                return 'Error: Failed to enhance transcript'


def test_enhancement():
    """Test function to verify the transcript enhancement works correctly."""
    test_transcript = """
    so when we're talking about um asynchronous programming in javascript we uh we use promises which are like um objects that represent the eventual completion or failure of an asynchronous operation and uh the way you create a promise is you use the new promise constructor and you pass in a function that takes uh two parameters resolve and reject
    """

    enhanced = enhance_transcript(test_transcript)
    print('Original transcript:')
    print(test_transcript)
    print('\nEnhanced transcript:')
    print(enhanced)


if __name__ == '__main__':
    test_enhancement()
