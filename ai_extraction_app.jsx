import React, { useState, useEffect } from 'react';
import { Download, Loader2, CheckCircle2, AlertCircle, Brain } from 'lucide-react';

export default function AIExtractionTool() {
  const [messages, setMessages] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [results, setResults] = useState([]);
  const [stats, setStats] = useState({ total: 0, processed: 0, noDoubts: 0 });

  useEffect(() => {
    // Load messages from the JSON file we prepared
    fetch('/mnt/user-data/outputs/all_messages_batch.jsonl')
      .then(response => response.text())
      .then(text => {
        const lines = text.trim().split('\n');
        const parsedMessages = lines.map(line => JSON.parse(line));
        setMessages(parsedMessages);
        setStats(prev => ({ ...prev, total: parsedMessages.length }));
      })
      .catch(err => console.error('Error loading messages:', err));
  }, []);

  const analyzeWithClaude = async (message) => {
    const prompt = `You are analyzing a Telegram message from Sheikh Hassan Al-Daghriri's Islamic education channel in Saudi Arabia. Your task is to extract structured data with HIGH ACCURACY.

**MESSAGE DETAILS:**
Filename: ${message.filename}
Clip Length: ${message.clip_length}
Gregorian Date: ${message.greg_date}

**MESSAGE TEXT:**
${message.message_text}

**IMPORTANT CONTEXT:**
1. Most entries are "Series" (weekly Islamic lessons on specific books), NOT individual lectures
2. "Khutba" are Friday sermons - marked with #خطبة_الجمعة or خطبة
3. "Lecture" are standalone talks - marked with محاضرة
4. For Series: Topic field should be "Not Available" (we track SeriesName and SubTopic instead)
5. For Khutba/Lecture: Extract the specific topic
6. SubTopics are chapter names like "كتاب النكاح", "باب الصلاة"
7. Serial numbers can be Arabic words (الأول، الثاني، الثالث والتسعون) or numerals
8. Most lessons are at "جامع الورود" (the masjid), only mark "Online" if text explicitly mentions "عن بُعد" or "بُعد"
9. Sheikh is ALWAYS: حسن بن محمد منصور الدغريري

**WEEKLY SCHEDULE (for context):**
Saturday after Asr: التفسير الميسر, تأسيس الأحكام شرح عمدة الأحكام (by أحمد النجمي)
Saturday after Maghrib: شرح السنة للبربهاري
Sunday after Asr: الملخص شرح كتاب التوحيد (by صالح الفوزان), تأسيس الأحكام
Sunday after Isha: الأفنان الندية (by زيد المدخلي)
Monday after Asr: الملخص الفقهي (by صالح الفوزان)
Monday after Isha: الأفنان الندية
Tuesday after Asr: الملخص شرح كتاب التوحيد
Tuesday after Isha: منظومة سلم الوصول (by حافظ حكمي)
Wednesday after Asr: الملخص الفقهي
Wednesday after Isha: تأسيس الأحكام
Friday: خطبة الجمعة

**CATEGORY DEFINITIONS:**
- Fiqh: Islamic jurisprudence (الملخص الفقهي, الأفنان الندية, فقه topics)
- Aqeedah: Islamic creed/belief (التوحيد, السنة, عقيدة topics)
- Hadeeth: Prophetic traditions (تأسيس الأحكام/عمدة الأحكام is Hadeeth)
- Other: General Islamic topics, Khutbas, standalone lectures

**EXTRACTION RULES:**
1. Type: Must be exactly "Khutba", "Lecture", or "Series"
2. Topic: Extract ONLY for Khutba/Lecture. For Series use "Not Available"
3. SeriesName: Full book name (e.g., "تأسيس الأحكام شرح عمدة الأحكام")
4. SubTopic: Chapter/section within the series (e.g., "كتاب النكاح (١)")
5. Serial: Lesson number - keep in Arabic if given that way
6. OriginalAuthor: The book's author (e.g., "أحمد بن يحيى النجمي", "صالح الفوزان")
7. Location: "جامع الورود" (default) or "Online" (only if explicitly mentioned)
8. DateInArabic: Hijri date in any format found (e.g., "١٧ جمادى الآخرة ١٤٤٠هـ" or "٥/٢/١٤٤٧")
9. Category: "Fiqh", "Aqeedah", "Hadeeth", or "Other"
10. doubts: List any uncertainties, or "none" if completely confident

**OUTPUT FORMAT:**
Respond with ONLY a valid JSON object, no markdown, no explanation:
{
  "Type": "...",
  "Topic": "...",
  "SeriesName": "...",
  "SubTopic": "...",
  "Serial": "...",
  "OriginalAuthor": "...",
  "Location": "...",
  "DateInArabic": "...",
  "Category": "...",
  "doubts": "..."
}`;

    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          messages: [{ role: "user", content: prompt }],
          temperature: 0
        })
      });

      const data = await response.json();
      const text = data.content[0].text;
      
      // Remove markdown code blocks if present
      const cleanText = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      const analysis = JSON.parse(cleanText);
      
      return analysis;
    } catch (error) {
      console.error('Error calling Claude API:', error);
      return null;
    }
  };

  const processAllMessages = async () => {
    setProcessing(true);
    const newResults = [];

    for (let i = 0; i < messages.length; i++) {
      setCurrentIndex(i);
      const msg = messages[i];

      try {
        const analysis = await analyzeWithClaude(msg);

        if (analysis) {
          const record = {
            TelegramFileName: msg.filename,
            Type: analysis.Type || 'Not Available',
            Topic: analysis.Topic || 'Not Available',
            SeriesName: analysis.SeriesName || 'Not Available',
            SubTopic: analysis.SubTopic || 'Not Available',
            Serial: analysis.Serial || 'Not Available',
            OriginalAuthor: analysis.OriginalAuthor || 'Not Available',
            'Location/Online': analysis.Location || 'جامع الورود',
            Sheikh: 'حسن بن محمد منصور الدغريري',
            DateInArabic: analysis.DateInArabic || 'Not Available',
            DateInGreg: msg.greg_date || 'Not Available',
            ClipLength: msg.clip_length || 'Not Available',
            Category: analysis.Category || 'Not Available',
            doubtsStatus: analysis.doubts || 'unknown'
          };

          newResults.push(record);

          if (analysis.doubts === 'none') {
            setStats(prev => ({ ...prev, noDoubts: prev.noDoubts + 1 }));
          }
        }

        setStats(prev => ({ ...prev, processed: i + 1 }));
        setResults([...newResults]);

        // Small delay to avoid rate limits
        await new Promise(resolve => setTimeout(resolve, 500));

      } catch (error) {
        console.error(`Error processing message ${i + 1}:`, error);
      }
    }

    setProcessing(false);
  };

  const downloadCSV = () => {
    if (results.length === 0) return;

    const headers = Object.keys(results[0]);
    const csvContent = [
      headers.join(','),
      ...results.map(row =>
        headers.map(header => {
          const value = row[header] || '';
          return `"${value.toString().replace(/"/g, '""')}"`;
        }).join(',')
      )
    ].join('\n');

    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'extracted_data_ai_powered.csv';
    link.click();
  };

  const progress = messages.length > 0 ? (currentIndex / messages.length) * 100 : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-700 to-purple-700 p-8 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
                  <Brain className="w-10 h-10" />
                  AI-Powered Data Extraction
                </h1>
                <p className="text-xl opacity-90">استخراج البيانات بالذكاء الاصطناعي</p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold">{stats.total}</div>
                <div className="text-sm opacity-90">Total Messages</div>
              </div>
            </div>
          </div>

          {/* Stats Dashboard */}
          <div className="p-8 bg-gradient-to-r from-gray-50 to-gray-100">
            <div className="grid grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-xl shadow-md">
                <div className="text-gray-600 text-sm mb-1">Total Messages</div>
                <div className="text-3xl font-bold text-indigo-600">{stats.total}</div>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-md">
                <div className="text-gray-600 text-sm mb-1">Processed</div>
                <div className="text-3xl font-bold text-purple-600">{stats.processed}</div>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-md">
                <div className="text-gray-600 text-sm mb-1">No Doubts</div>
                <div className="text-3xl font-bold text-green-600">{stats.noDoubts}</div>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-md">
                <div className="text-gray-600 text-sm mb-1">Accuracy</div>
                <div className="text-3xl font-bold text-blue-600">
                  {stats.processed > 0 ? ((stats.noDoubts / stats.processed) * 100).toFixed(1) : 0}%
                </div>
              </div>
            </div>
          </div>

          {/* Processing Area */}
          <div className="p-8">
            {!processing && results.length === 0 && (
              <div className="text-center py-12">
                <Brain className="w-20 h-20 mx-auto mb-6 text-indigo-600" />
                <h2 className="text-2xl font-bold mb-4">Ready to Process {stats.total} Messages</h2>
                <p className="text-gray-600 mb-8">
                  Using Claude API for intelligent pattern recognition and maximum accuracy
                </p>
                <button
                  onClick={processAllMessages}
                  className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:shadow-xl transition-all transform hover:scale-105"
                >
                  Start AI Extraction
                </button>
              </div>
            )}

            {processing && (
              <div className="text-center py-12">
                <Loader2 className="w-16 h-16 mx-auto mb-6 text-indigo-600 animate-spin" />
                <h2 className="text-2xl font-bold mb-4">Processing Messages...</h2>
                <div className="mb-6">
                  <div className="text-lg text-gray-700 mb-2">
                    Message {currentIndex + 1} of {messages.length}
                  </div>
                  <div className="text-sm text-gray-500 mb-4">
                    {messages[currentIndex]?.filename}
                  </div>
                </div>
                <div className="max-w-2xl mx-auto">
                  <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-indigo-600 to-purple-600 h-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <div className="text-sm text-gray-600 mt-2">{progress.toFixed(1)}%</div>
                </div>
              </div>
            )}

            {!processing && results.length > 0 && (
              <div className="text-center py-12">
                <CheckCircle2 className="w-20 h-20 mx-auto mb-6 text-green-600" />
                <h2 className="text-2xl font-bold mb-4">Extraction Complete!</h2>
                <div className="grid grid-cols-3 gap-6 max-w-3xl mx-auto mb-8">
                  <div className="bg-green-50 p-6 rounded-xl">
                    <div className="text-4xl font-bold text-green-600 mb-2">{stats.noDoubts}</div>
                    <div className="text-sm text-gray-600">Records with No Doubts</div>
                  </div>
                  <div className="bg-yellow-50 p-6 rounded-xl">
                    <div className="text-4xl font-bold text-yellow-600 mb-2">
                      {stats.processed - stats.noDoubts}
                    </div>
                    <div className="text-sm text-gray-600">Records with Doubts</div>
                  </div>
                  <div className="bg-blue-50 p-6 rounded-xl">
                    <div className="text-4xl font-bold text-blue-600 mb-2">
                      {((stats.noDoubts / stats.processed) * 100).toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">Confidence Rate</div>
                  </div>
                </div>
                <button
                  onClick={downloadCSV}
                  className="bg-gradient-to-r from-green-600 to-blue-600 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:shadow-xl transition-all transform hover:scale-105 inline-flex items-center gap-3"
                >
                  <Download className="w-5 h-5" />
                  Download CSV Results
                </button>
              </div>
            )}
          </div>

          {/* Recent Results Preview */}
          {results.length > 0 && (
            <div className="p-8 bg-gray-50 border-t">
              <h3 className="text-xl font-bold mb-4">Recent Results (Last 5)</h3>
              <div className="space-y-3">
                {results.slice(-5).reverse().map((result, idx) => (
                  <div key={idx} className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="font-semibold text-lg text-gray-800 mb-1">
                          {result.TelegramFileName}
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div><span className="text-gray-600">Type:</span> <span className="font-medium">{result.Type}</span></div>
                          <div><span className="text-gray-600">Series:</span> <span className="font-medium">{result.SeriesName}</span></div>
                          <div><span className="text-gray-600">Serial:</span> <span className="font-medium">{result.Serial}</span></div>
                          <div><span className="text-gray-600">Category:</span> <span className="font-medium">{result.Category}</span></div>
                        </div>
                      </div>
                      <div>
                        {result.doubtsStatus === 'none' ? (
                          <CheckCircle2 className="w-6 h-6 text-green-600" />
                        ) : (
                          <AlertCircle className="w-6 h-6 text-yellow-600" />
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
