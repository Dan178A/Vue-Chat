import express from 'express';
import cors from 'cors';
import { Request, Response } from 'express';
import { OpenAI } from 'openai';

// express configuration--------------------------------------------------------------
const app = express();
const port = 5000;

// enable CORS
app.use(cors());

// openai chatGPT configuration--------------------------------------------------------------
const openai: any = new OpenAI({ apiKey: 'your-api-key' }); // replace 'your-api-key' with your actual OpenAI API key
const allMessages: { [key: string]: any[] } = {};

app.post('/get_answer', (req: Request, res: Response) => {
  console.log(req.body,req)
  // const prompt = req.body.prompt;
  // const botName = req.body.bot;

  // const answer = getAnswerFromBot(botName, prompt);

  res.json({
    status: 'success',
    answer: ''
  });
});

function getAnswerFromBot(botName: string, prompt: string): string {
  let messages = allMessages[botName];
  if (!messages) {
    console.log(`allMessages[${botName}] is undefined, so initialize it.`);
    allMessages[botName] = [];
    messages = allMessages[botName];
  }

  messages.push({
    role: 'user',
    content: prompt,
  });
  console.log(`user: ${prompt}`);

  const completion = openai.createCompletion({
    model: 'gpt-3.5-turbo',
    messages: messages,
  });

  const message = completion.choices[0].message;
  messages.push(message);
  console.log(`${botName}: ${message.content}`);

  return message.content;
}

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});