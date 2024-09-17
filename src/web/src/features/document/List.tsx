import React, { useEffect, useState } from "react";
import { Table, Typography, Spin, Alert } from "antd";
import axios from "axios";

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

const DocumentTable: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const response = await axios.get(
          "https://localhost:1002/api/Documents",
          {
            headers: {
              Accept: "application/json",
            },
          }
        );
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

    fetchDocuments();
  }, []);

  if (loading) return <Spin size="large" />;
  if (error) return <Alert message="Error" description={error} type="error" />;

  return (
    <div>
      <Title level={2}>Document Table</Title>
      <Table columns={columns} dataSource={documents} rowKey="id" />
    </div>
  );
};

export default DocumentTable;
