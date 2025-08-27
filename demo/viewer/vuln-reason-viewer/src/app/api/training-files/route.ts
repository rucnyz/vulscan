import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // 训练数据存放在training目录中
    const dataDir = path.join(process.cwd(), 'data', 'training');
    
    // 确保目录存在
    if (!fs.existsSync(dataDir)) {
      console.log(`Training data directory does not exist, creating: ${dataDir}`);
      try {
        fs.mkdirSync(dataDir, { recursive: true });
        console.log(`Successfully created directory: ${dataDir}`);
        return NextResponse.json({ 
          files: [],
          message: "Training directory was created. Please add training data files."
        });
      } catch (dirError) {
        console.error(`Failed to create training directory: ${dirError}`);
        return NextResponse.json({ 
          error: 'Failed to create training directory', 
          files: [] 
        }, { status: 500 });
      }
    }
    
    // 读取训练目录中的所有文件
    const files = fs.readdirSync(dataDir)
      .filter(file => file.endsWith('.json')) // 只包含JSON文件
      .sort(); // 按字母顺序排序
    
    return NextResponse.json({ 
      files,
      directory: dataDir
    });
  } catch (error) {
    console.error('Error listing training files:', error);
    return NextResponse.json(
      { error: 'Failed to list training files', files: [] }, 
      { status: 500 }
    );
  }
} 