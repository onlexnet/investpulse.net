package net.investpulse.sentiment.persistence;

import org.apache.parquet.io.OutputFile;
import org.apache.parquet.io.PositionOutputStream;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;

/**
 * Minimal {@link OutputFile} implementation using direct Java NIO.
 * Bypasses Hadoop's security framework completely.
 */
public class LocalOutputFile implements OutputFile {
    
    private final File file;

    public LocalOutputFile(File file) {
        this.file = file;
    }

    @Override
    public PositionOutputStream create(long blockSizeHint) throws IOException {
        // Ensure parent directories exist
        if (file.getParentFile() != null && !file.getParentFile().exists()) {
            Files.createDirectories(file.getParentFile().toPath());
        }
        return new LocalPositionOutputStream(new FileOutputStream(file));
    }

    @Override
    public PositionOutputStream createOrOverwrite(long blockSizeHint) throws IOException {
        return create(blockSizeHint);
    }

    @Override
    public boolean supportsBlockSize() {
        return false;
    }

    @Override
    public long defaultBlockSize() {
        return 0;
    }

    /**
     * Wraps {@link FileOutputStream} to track position for Parquet.
     */
    private static class LocalPositionOutputStream extends PositionOutputStream {
        private final FileOutputStream outputStream;
        private long position = 0;

        LocalPositionOutputStream(FileOutputStream outputStream) {
            this.outputStream = outputStream;
        }

        @Override
        public long getPos() {
            return position;
        }

        @Override
        public void write(int b) throws IOException {
            outputStream.write(b);
            position++;
        }

        @Override
        public void write(byte[] b) throws IOException {
            outputStream.write(b);
            position += b.length;
        }

        @Override
        public void write(byte[] b, int off, int len) throws IOException {
            outputStream.write(b, off, len);
            position += len;
        }

        @Override
        public void flush() throws IOException {
            outputStream.flush();
        }

        @Override
        public void close() throws IOException {
            outputStream.close();
        }
    }
}
