import React, { useEffect, useState } from "react";
import { Table, Typography, Spin, Alert } from "antd";
import { RcFile } from "antd/es/upload";
import axios from "axios";
import { App, Button, Upload, UploadProps } from "antd";
import { UploadOutlined } from "@ant-design/icons";
const { Title } = Typography;

interface Document {
  id: number;
  fileName: string;
  contentType: string;
  filePath: string;
  ownerId: string;
  uploadedDate: string;
  status: string;
}

interface ApiResponse {
  isSucceed: boolean;
  messages: Record<string, any>;
  data: {
    documents: Document[];
  };
}

const columns = [
  {
    title: "File Name",
    dataIndex: "fileName",
    key: "fileName",
  },
  {
    title: "Content Type",
    dataIndex: "contentType",
    key: "contentType",
  },
  {
    title: "File Path",
    dataIndex: "filePath",
    key: "filePath",
  },
  {
    title: "Uploaded Date",
    dataIndex: "uploadedDate",
    key: "uploadedDate",
  },
  {
    title: "Status",
    dataIndex: "status",
    key: "status",
  },
];

const DocumentDashboard: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { message } = App.useApp();
  const BASE_URL = "https://localhost:1002";

  const props: UploadProps = {
    name: "file",
    customRequest: async (options: any) => {
      const { file, onSuccess, onError } = options;

      const formData = new FormData();
      formData.append("file", file as RcFile);
      try {
        const response = await axios.post(
          `${BASE_URL}/api/Documents`,
          formData,
          {
            headers: {
              // Add any headers you might need (e.g., authorization)
              // 'Authorization': `Bearer ${token}`
            },
          }
        );

        if (response.status === 200) {
          // Axios returns status in `response.status`
          const data = response.data; // Axios automatically parses JSON
          onSuccess?.(data, file);
          // message.success(`${(file as RcFile).name} file uploaded successfully`);
        } else {
          throw new Error("Upload failed");
        }
      } catch (error) {
        onError?.(error instanceof Error ? error : new Error("Upload failed"));
        message.error(`${(file as RcFile).name} file upload failed.`);
      }
    },
    onChange(info) {
      if (info.file.status !== "uploading") {
        console.log(info.file, info.fileList);
      }
      if (info.file.status === "done") {
        message.success(`${info.file.name} file uploaded successfully`);
        fetchDocuments();
      } else if (info.file.status === "error") {
        message.error(`${info.file.name} file upload failed.`);
      }
    },
  };
  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${BASE_URL}/api/Documents`, {
        headers: {
          Accept: "application/json",
        },
      });
      setLoading(false);
      const result: ApiResponse = response.data;
      if (result.isSucceed) {
        setDocuments(result.data.documents);
      } else {
        setError("Failed to load documents");
      }
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "An unknown error occurred"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  if (loading) return <Spin size="large" />;
  if (error) return <Alert message="Error" description={error} type="error" />;

  return (
    <div>
      <Title level={2}>Document Dashboard</Title>
      <Upload {...props}>
        <Button icon={<UploadOutlined />}>Click to Upload</Button>
      </Upload>
      <Table
        columns={columns}
        dataSource={documents}
        rowKey="id"
        className="mt-3"
      />
    </div>
  );
};

export default DocumentDashboard;
