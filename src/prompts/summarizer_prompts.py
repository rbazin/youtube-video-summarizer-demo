CHUNK_SUMMARIZER_PROMPT = """Your task is to summarize the key information from a transcript chunk (an excerpt from the transcript of a YouTube video, typically 1000 words long) in the form of clear, concise bullet points and a title. 

Follow these steps:

1. Carefully read the transcript chunk to identify the most important points, arguments, takeaways, and conclusions. 
2. Organize the key information into a logical bullet point structure.
3. Write the summary and title, following these specifications:
    - The bullet point summary should:
        - Capture the essential information needed to understand the main points 
        - Be concise yet comprehensive (aim for 4-7 bullet points, each 1-2 sentences long)
        - Maintain logical coherence 
    - The title should:
        - Concisely summarize the main topic or overarching message of the chunk
        - Be 5-10 words long
    - Write in the same language as the input chunk

Provide your output in this JSON format:
<json>
{
  "scratchpad": "Your notes and thoughts for steps 1 and 2 go here.",
  "summary": "## Chunk Title\n\nBullet point 1\nBullet point 2\n...",
}
</json>

Example of desired output for a transcript chunk about the benefits of meditation:
<example_json>
{
  "scratchpad": "Key points: meditation reduces stress, anxiety, depression; improves focus, memory, emotional regulation; enhances self-awareness, well-being; short daily sessions effective. \nMain takeaway: meditation provides significant mental health and cognitive benefits.\nLogical bullet point structure: 1) Mental health benefits 2) Cognitive improvements 3) Self-awareness and well-being 4) Effective even in short sessions",
  "summary": "## The Science-Backed Benefits of Meditation\n\nMeditation can reduce stress, anxiety and depression symptoms\nRegular practice improves focus, memory and emotional regulation\nMeditation enhances self-awareness and overall well-being\nEven short daily meditation sessions of 10 minutes can provide benefits",
}
</example_json>

Note: even if your input is empty, please provide a valid JSON object with the keys "scratchpad", "summary" to maintain consistency.
Note: to generate a valid JSON object, be extra cautious to start your JSON object with `{` and end it with `}`.
Note: don't forget to write the summary in the "summary" key/value of the JSON object.
"""

SUMMARIES_MERGER_PROMPT = """Your task is to compile the individual chunk summaries from a YouTube video transcript into a coherent, well-structured, and insightful overall summary. The summary should include a main title, sub-sections with sub-titles, and informative bullet points that capture the key ideas and takeaways from the video.

Follow these steps:

1. Review all the individual chunk summaries to identify overarching themes, main arguments, and crucial conclusions.
2. Group related points together and organize them into logical sub-sections.
3. Write the comprehensive summary, following these specifications:
   - Main Title:
     - Concisely capture the central topic or main message of the entire video
     - Should be attention-grabbing and informative
     - Aim for 5-10 words
   - Sub-Sections:
     - Organize the content into logical sub-sections based on the overarching themes or main points identified
     - Each sub-section should have a clear and descriptive sub-title
     - Aim for 3-5 sub-sections, depending on the length and complexity of the video
   - Bullet Points:
     - Under each sub-section, present the key ideas, arguments, and takeaways as concise and informative bullet points
     - Ensure the bullet points capture the essential information while maintaining logical coherence within and between sub-sections
     - Aim for 3-6 bullet points per sub-section
   - Language:
     - Write in the same language as the input chunk summaries
     - Use clear, concise, and engaging language that effectively conveys the main ideas

Provide your output in this JSON format:
<json>
{
  "scratchpad": "Your notes and thoughts for steps 1 and 2 go here.",
  "summary": "# Main Title\n\n## Sub-Title 1\n- Bullet point 1\n- Bullet point 2\n...\n\n## Sub-Title 2\n- Bullet point 1\n- Bullet point 2\n...",
}
</json>

Example of desired output for a video about the benefits and techniques of meditation:
<example_json>
{
  "scratchpad": "Overarching themes: mental health benefits, cognitive improvements, self-awareness, getting started with meditation\nMain points: reduces stress/anxiety/depression, improves focus/memory/emotional regulation, enhances well-being, short sessions effective, simple techniques\nSub-sections: 1) Mental health benefits 2) Cognitive benefits 3) Meditation and self-awareness 4) Getting started",
  "summary": "# The Power of Meditation: Improve Your Mind and Well-Being\n\n## Mental Health Benefits\n- Meditation can significantly reduce symptoms of stress, anxiety, and depression\n- Regular practice helps regulate emotions and promotes a more positive mood\n- Meditation can be an effective complementary treatment for various mental health conditions\n\n## Cognitive Improvements\n- Consistent meditation practice enhances focus, attention, and memory retention\n- Meditators often experience improved problem-solving and decision-making skills\n- Meditation can help maintain cognitive function and may slow age-related cognitive decline\n\n## Meditation and Self-Awareness\n- Practicing meditation cultivates a deeper sense of self-awareness and introspection\n- Meditators often report increased emotional intelligence and better self-regulation\n- Meditation can foster a greater sense of connection and empathy towards others\n\n## Getting Started with Meditation\n- Even short daily meditation sessions of 10-15 minutes can provide significant benefits\n- Simple techniques like focusing on the breath or a mantra can be powerful starting points\n- Consistency and patience are key to establishing a sustainable meditation practice"
}
</example_json>

Note: even if your input is empty, please provide a valid JSON object with the keys "scratchpad" and "summary", and empty strings "" as values, to maintain consistency.
Note: to generate a valid JSON object, be extra cautious to start your JSON object with `{` and end it with `}`.
Note: don't forget to write the summary in the "summary" key/value of the JSON object.
"""
