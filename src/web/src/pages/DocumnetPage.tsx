import { App, Breadcrumb, Button, Upload, UploadProps } from "antd";
import { UploadOutlined } from "@ant-design/icons";

export const DocumentPage = () => {
  const { message } = App.useApp();
  const BASE_URL = "https://localhost:1002";

  const props: UploadProps = {
    name: "file",
    action: `${BASE_URL}/api/Documents`,
    onChange(info) {
      if (info.file.status !== "uploading") {
        console.log(info.file, info.fileList);
      }
      if (info.file.status === "done") {
        message.success(`${info.file.name} file uploaded successfully`);
      } else if (info.file.status === "error") {
        message.error(`${info.file.name} file upload failed.`);
      }
    },
  };

  return (
    <>
      <Breadcrumb
        style={{ margin: "16px 0" }}
        items={[{ key: 1, title: "Document Dashboard", separator: "/" }]}
      ></Breadcrumb>
      <Upload {...props}>
        <Button icon={<UploadOutlined />}>Click to Upload</Button>
      </Upload>
    </>
  );
};
/*
  const response = await axios.post(`${BASE_URL}/user/profile`).catch((ex)=>{
    console.log(ex);
  });
import React from 'react';
import { UploadOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { Button, message, Upload } from 'antd';

const props: UploadProps = {
  name: 'file',
  action: 'https://660d2bd96ddfa2943b33731c.mockapi.io/api/upload',
  headers: {
    authorization: 'authorization-text',
  },
  onChange(info) {
    if (info.file.status !== 'uploading') {
      console.log(info.file, info.fileList);
    }
    if (info.file.status === 'done') {
      message.success(`${info.file.name} file uploaded successfully`);
    } else if (info.file.status === 'error') {
      message.error(`${info.file.name} file upload failed.`);
    }
  },
};

const App: React.FC = () => (
  <Upload {...props}>
    <Button icon={<UploadOutlined />}>Click to Upload</Button>
  </Upload>
);

export default App;

*/
