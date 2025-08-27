import { NextResponse } from 'next/server';
import { ResultData, ConversationData } from '@/lib/types';
import fs from 'fs';
import path from 'path';

export async function GET(request: Request) {
  try {
    // 从查询参数中获取文件名
    const { searchParams } = new URL(request.url);
    const filename = searchParams.get('file') || 'training.json'; // 如果未指定则默认为training.json
    
    // 确保文件名经过净化，防止目录遍历攻击
    const sanitizedFilename = path.basename(filename);
    
    // 只允许.json文件
    if (!sanitizedFilename.endsWith('.json')) {
      return NextResponse.json({ error: 'Invalid file format' }, { status: 400 });
    }
    
    // 训练数据存放在training子目录
    const filePath = path.join(process.cwd(), 'data', 'training', sanitizedFilename);
    
    // 检查文件是否存在
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({ error: 'Training file not found' }, { status: 404 });
    }
    
    const fileContents = fs.readFileSync(filePath, 'utf8');
    
    // 解析JSON数据
    const data = JSON.parse(fileContents);
    
    // 检查数据格式并适配
    // 如果数据是对话格式，直接返回
    if (data && 'conversations' in data && Array.isArray(data.conversations)) {
      return NextResponse.json(data);
    }
    
    // 如果数据是数组，直接返回
    if (Array.isArray(data)) {
      return NextResponse.json(data);
    }
    
    // 如果数据不符合ResultData类型，尝试将其转换为该类型
    if (!data.results) {
      return NextResponse.json({
        model: "Unknown",
        task: {
          dataset: sanitizedFilename.replace('.json', ''),
          language: "unknown",
          prompt_type: "unknown"
        },
        metrics: {},
        results: Array.isArray(data) ? data : [data]
      });
    }
    
    // 对于符合ResultData类型的数据，直接返回
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error loading training results:', error);
    return NextResponse.json({ error: 'Failed to load training data' }, { status: 500 });
  }
} 