package example.vcb;

class JobController {
    Job getJob(String jobId) {
        return jobService.find(jobId);
    }

    Job closeJob(String jobId, CloseRequest request) {
        return jobService.close(jobId, request.reason());
    }
}

record CloseRequest(String reason, String requestId, String sceneType, String sceneChatId) {}
record Job(String id, String ownerOpenId, String status) {}

