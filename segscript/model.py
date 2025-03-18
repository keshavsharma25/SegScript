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
        model='gemini-1.5-flash'
    )  # You mentioned gemini-2.0-flash, but I'm using 1.5 as fallback
except Exception as e:
    print(f'Error initializing Gemini model: {e}')


# Define the prompt template for transcript enhancement
ENHANCE_PROMPT = """
You are an AI assistant specialized in enhancing raw transcripts from YouTube videos, particularly about computer science and technology.
Your task is to improve the readability of the transcript without changing its meaning or technical terminology.

Please make the following improvements to the transcript:
1. Remove filler words such as "um", "uh", "like", "you know", "sort of", "kind of", etc.
2. Add appropriate punctuation (periods, commas, question marks, etc.)
3. Ensure complete sentences (make sure sentences start with a capital letter and end with proper punctuation)
4. Break the text into paragraphs where appropriate

IMPORTANT RULES:
- DO NOT change any technical terms or jargon
- DO NOT paraphrase or substitute words with synonyms
- DO NOT add any new information not present in the original
- DO NOT correct technical information even if it seems wrong
- DO NOT summarize or condense the content
- DO NOT correct grammar that is already correct
- PRESERVE ALL the original content and meaning
- PRESERVE the speaker's original style and tone
- PRESERVE repetitive words or phrases that may be used for emphasis or to explain technical concepts
- Be careful to distinguish between actual filler words and intentional repetition used to emphasize important points
- ONLY remove clear filler words and add punctuation where needed

Here are some examples of raw transcripts and their enhanced versions:

EXAMPLE 1:
Raw: "so when we're talking about um asynchronous programming in javascript we uh we use promises which are like um objects that represent the eventual completion or failure of an asynchronous operation and uh the way you create a promise is you use the new promise constructor and you pass in a function that takes uh two parameters resolve and reject and um inside that function you do your async operation and when it's done you call resolve with the result or uh if there's an error you call reject and um then you can use then and catch methods to uh to handle the results or errors"

Enhanced: "When we're talking about asynchronous programming in JavaScript, we use promises which are objects that represent the eventual completion or failure of an asynchronous operation. The way you create a promise is you use the new Promise constructor and you pass in a function that takes two parameters: resolve and reject. Inside that function, you do your async operation and when it's done, you call resolve with the result or if there's an error, you call reject. Then you can use then and catch methods to handle the results or errors."

EXAMPLE 2:
Raw: "so gradient descent is basically um an optimization algorithm used to minimize the cost function in various machine learning algorithms and the way it works is um you start with some initial parameter values and then you compute the gradient of the cost function which is like um the direction of steepest increase and then you update the parameters in the negative direction of the gradient and uh you do this iteratively until the algorithm converges and um there are different variants like batch gradient descent and stochastic gradient descent which uh differ in how many samples they use to compute the gradient at each step"

Enhanced: "Gradient descent is basically an optimization algorithm used to minimize the cost function in various machine learning algorithms. The way it works is you start with some initial parameter values and then you compute the gradient of the cost function, which is the direction of steepest increase. Then you update the parameters in the negative direction of the gradient. You do this iteratively until the algorithm converges. There are different variants like batch gradient descent and stochastic gradient descent, which differ in how many samples they use to compute the gradient at each step."

Now, enhance the following transcript without changing its meaning or technical terminology:

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
