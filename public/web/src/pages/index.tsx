import AsyncButton from '@/components/AsyncButton';
import { Button, List, Space, Upload, UploadFile, message } from 'antd'
import axios from 'axios';
import { useEffect, useState } from 'react';

export default function HomePage() {
  const [list, setList] = useState<{ filename: string; url: string }[]>([])
  const [files, setFiles] = useState<UploadFile[]>([])

  const fetchList = () => {
    axios.get('/apis/files/query').then(({ data }: any) => {
      setList(data.data || [])
    })
  }

  useEffect(() => {
    fetchList()
  }, [])


  const onTransition = async (fileUrl: string, type: 'word' | 'excel') => {
    const res = await axios.post('/apis/pdf/transition', { fileUrl, type }).then(res => res.data);
    if (res.data) {
      const link = document.createElement('a')
      link.href = download(res.data)
      document.body.appendChild(link);
      link.click();
    } else {
      message.warning('转换失败')
    }
  }
  const download = (path: string) => `/apis/download${path}`

  const onDelete = async (path: string) => {
    const res = await axios.delete('/apis/files/delete' + path).then(res=>res.data)
    fetchList()
  }
  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <div style={{ width: '50%' }}>
          <div style={{ padding: 28, textAlign: 'center' }}>
            <Upload
              action='/apis/upload'
              fileList={files}
              showUploadList={false}
              onChange={({ fileList }) => {
                let count = 0
                fileList.forEach(item => item.status == 'done' ? count++ : null)
                if (count == fileList.length) {
                  setFiles([])
                  fetchList();
                  return
                }
                setFiles(fileList)
              }}>
              <Button type='primary' loading={Boolean(files.length)}>上传文件</Button>
            </Upload>
          </div>
          <List>
            {
              list.map(item => {
                const isPdf = item.filename.includes('.pdf')
                return <List.Item
                  key={item.url}
                  children={<a href={download(item.url)} download={false} target='_blank'>{item.filename}</a>}
                  extra={
                    <Space>
                      <Button type='link' href={download(item.url)} download={true}>下载</Button>
                      {
                        isPdf && <AsyncButton type='link' onClick={async () => await onTransition(item.url, 'word')}>转换成word</AsyncButton>
                      }
                      {
                        isPdf && <AsyncButton type='link' onClick={async () => await onTransition(item.url, 'excel')}>转换成excel</AsyncButton>
                      }
                      <AsyncButton onClick={async () => await onDelete(item.url)} type='link' danger>删除</AsyncButton>
                    </Space>
                  }
                />
              })
            }
          </List>
        </div>
      </div>
    </>
  );
}
